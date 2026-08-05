from __future__ import annotations

from collections import Counter
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
import vizro_dash_components as vdc
from dash import html
from pydantic import BeforeValidator, Field, PrivateAttr, TypeAdapter, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    ActionsType,
    MultiValueType,
    SingleValueType,
    _IdProperty,
)

_LEAF_ADAPTER: TypeAdapter[SingleValueType] = TypeAdapter(SingleValueType)


def _coerce_cascader_leaf_scalar(item: Any) -> Any:
    """Coerce a leaf to `SingleValueType` so it matches how `value` gets validated (e.g. Timestamp → date)."""
    try:
        return _LEAF_ADAPTER.validate_python(item)
    except Exception as exc:
        raise ValueError(
            "Cascader leaf lists must contain only scalar values "
            "(str, number, bool, or date), not dicts or nested structures."
        ) from exc


def _walk_cascader_branch(node: Any, *, path: str) -> None:
    if isinstance(node, dict):
        for key, child in node.items():
            _walk_cascader_branch(child, path=f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        if not node:
            raise ValueError(
                f"Cascader options at '{path or 'root'}' contain an empty leaf list; provide at least one scalar leaf."
            )
        # Coerce in place so options and `value` share the same scalar type after validation.
        for i, item in enumerate(node):
            node[i] = _coerce_cascader_leaf_scalar(item)
    else:
        raise ValueError(
            f"Cascader options at '{path or 'root'}' must be a nested dict or a list of scalars, "
            f"not {type(node).__name__}."
        )


# Options are not a uniform recursive dict[str, T] (e.g. JSON-style trees): branch nodes are dict[str, …] but
# leaves are list[scalar], so the shape is dict[str, dict[str, …] | list[SingleValueType]]. A forward-ref union
# can express that in Pydantic, but we still need imperative validation for rules a single type does not capture:
# root must be a non-empty dict (not a list), leaf lists must be non-empty, every leaf item must match
# SingleValueType, and the tree must contain at least one leaf. The same helpers (e.g. walking the tree and
# collecting leaves in depth-first order) are required elsewhere anyway.
#
# This validator is mode-agnostic (structure only); the leaf-mode duplicate-leaf restriction is enforced later in
# `_validate_value` where `full_path` is known (path mode allows duplicate leaves).
def validate_cascader_options(data: Any) -> Any:
    """Ensure options are a nested dict with scalar-only leaf lists; reject root list and empty trees."""
    if not isinstance(data, dict):
        raise ValueError("Cascader options must be a nested dictionary (not a list).")
    if not data:
        # Empty dict is allowed so vm.Filter can defer filling options in `pre_build`.
        return data
    _walk_cascader_branch(data, path="")
    leaves = _iter_cascader_leaves_depth_first(data)
    if not leaves:
        raise ValueError("Cascader options must contain at least one leaf value.")
    return data


def _iter_cascader_leaves_depth_first(options: dict[str, Any]) -> list[SingleValueType]:
    leaves: list[SingleValueType] = []
    for value in options.values():
        if isinstance(value, list):
            leaves.extend(cast(list[SingleValueType], value))
        else:
            leaves.extend(_iter_cascader_leaves_depth_first(value))
    return leaves


def _iter_cascader_paths_depth_first(
    options: dict[str, Any], _prefix: tuple[Any, ...] = ()
) -> list[list[SingleValueType]]:
    """Yield the full root-to-leaf path for every leaf in depth-first order.

    Branch labels (dict keys) form the path prefix and the leaf scalar is the last element, so
    `{"Region": {"East": [1, 2]}}` yields `[["Region", "East", 1], ["Region", "East", 2]]`.
    """
    paths: list[list[SingleValueType]] = []
    for key, value in options.items():
        prefix = (*_prefix, key)
        if isinstance(value, list):
            paths.extend([*prefix, leaf] for leaf in value)
        else:
            paths.extend(_iter_cascader_paths_depth_first(value, prefix))
    return paths


def _normalize_cascader_path(path: Any) -> tuple[Any, ...]:
    """Path key for membership tests: branch labels stringified, leaf kept typed.

    Options built from a dataframe stringify branch labels but keep leaves typed, so branches must be
    compared as `str` while the leaf keeps its type:
    >>> _normalize_cascader_path([1, 2, 3])  # ("1", "2", 3)
    """
    path = list(path)
    return (*(str(segment) for segment in path[:-1]), path[-1])


def _reject_duplicate_leaves(leaves: list[SingleValueType]) -> None:
    """Leaf-mode only: forbid the same leaf label under more than one branch.

    In leaf mode a selection is addressed by its bare leaf value, so a duplicate leaf is ambiguous. Path mode
    (full_path=True) addresses selections by their full root-to-leaf path and therefore allows duplicate leaves.
    """
    if duplicates := [value for value, count in Counter(leaves).items() if count > 1]:
        raise ValueError(
            f"Cascader options must not contain duplicate leaf values: {duplicates}. "
            "Set full_path=True to address selections by their full root-to-leaf path instead."
        )


def _validate_full_path(path: Any, valid_paths: set[tuple[Any, ...]]) -> list[SingleValueType]:
    """Return `path` as a list if it is a non-empty valid root-to-leaf path, else raise."""
    if not path or _normalize_cascader_path(path) not in valid_paths:
        raise ValueError("Please provide a valid value from `options`.")
    return list(path)


def _validate_leaf_value(value: Any, leaves: set[Any], *, multi: bool) -> Any:
    """Leaf mode (full_path=False): validate `value` and return it in canonical form.

    `value` is a leaf scalar (single) or a list of leaf scalars (multi). A path (list) for a single-select, or a
    list of paths (list of lists) for a multi-select, is rejected — that is the path-mode shape and requires
    full_path=True. For a multi-select a bare scalar is normalized to a single-element list so the stored value
    matches the multi component shape (important for the "Reset controls" original value). `leaves` is a set for
    O(1) membership.
    """
    if not multi:
        if isinstance(value, list):
            raise ValueError(
                "A single-select Cascader with full_path=False expects a leaf value (e.g. 'France'), not a path. "
                "Set full_path=True to select by full path, or multi=True to select multiple leaves."
            )
        if value not in leaves:
            raise ValueError("Please provide a valid value from `options`.")
        return value

    # multi=True: accept a bare scalar (normalized to a list below) or a list of leaf scalars, but reject paths.
    items = value if isinstance(value, list) else [value]
    for item in items:
        if isinstance(item, list):
            raise ValueError(
                "A multi-select Cascader with full_path=False expects a list of leaf values "
                "(e.g. ['France', 'Japan']), not paths. Set full_path=True to select by full path."
            )
        if item not in leaves:
            raise ValueError("Please provide a valid value from `options`.")
    return items


def _validate_path_value(value: Any, options: dict[str, Any], *, multi: bool) -> None:
    """Path mode (full_path=True): `value` is a full path (single) or a list of full paths (multi).

    A bare leaf scalar (single) or a list of bare leaves (multi) is rejected — that is the leaf-mode shape and
    requires full_path=False. Paths are validated strictly against `options`; there is no leaf-to-path resolution.
    """
    valid_paths = {_normalize_cascader_path(path) for path in _iter_cascader_paths_depth_first(options)}
    if not multi:
        if not isinstance(value, list):
            raise ValueError(
                "A single-select Cascader with full_path=True expects a full root-to-leaf path "
                "(e.g. ['Europe', 'France']), not a bare leaf. Set full_path=False to select by leaf value."
            )
        if any(isinstance(item, list) for item in value):
            raise ValueError("Please set multi=True if providing a list of paths.")
        _validate_full_path(value, valid_paths)
        return

    # multi=True: value must be a list of paths (a list of lists).
    if not isinstance(value, list):
        raise ValueError(
            "A multi-select Cascader with full_path=True expects a list of full root-to-leaf paths "
            "(e.g. [['Europe', 'France']])."
        )
    for item in value:
        if not isinstance(item, list):
            raise ValueError(
                "A multi-select Cascader with full_path=True expects a list of full root-to-leaf paths "
                "(e.g. [['Europe', 'France']]), not bare leaves. Set full_path=False to select by leaf value."
            )
        _validate_full_path(item, valid_paths)


# `get_cascader_default_value` uses the leaves/paths under the first root key in depth-first order: single-select
# takes the first; multi-select takes the full list.
def get_cascader_default_value(
    options: dict[str, Any], *, multi: bool, full_path: bool = False
) -> SingleValueType | MultiValueType | list[SingleValueType] | list[list[SingleValueType]]:
    if not options:
        raise ValueError("Cascader options must be non-empty before a default value can be computed.")

    if full_path:
        first_key = next(iter(options))
        first_branch_paths = _iter_cascader_paths_depth_first({first_key: options[first_key]})
        return first_branch_paths if multi else first_branch_paths[0]

    first_value = next(iter(options.values()))
    if isinstance(first_value, list):
        leaves = cast(list[SingleValueType], list(first_value))
    else:
        leaves = _iter_cascader_leaves_depth_first(first_value)
    if multi:
        return cast(MultiValueType, list(leaves))
    return leaves[0]


class Cascader(VizroBaseModel):
    """Cascader selector for [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [Hierarchical selectors](../user-guides/selectors.md#hierarchical-selectors)

    """

    type: Literal["cascader"] = "cascader"
    full_path: bool = Field(
        default=False,
        frozen=True,
        description="How a selection is identified. In leaf mode (False, default) `value` is a bare leaf scalar "
        "(single-select) or a list of leaf scalars (multi-select), and leaf labels must be unique across the tree. "
        "In path mode (True) `value` is a full root-to-leaf path (single-select) or a list of paths (multi-select), "
        "so duplicate leaf labels across different branches are addressed unambiguously. This attribute is "
        "immutable once set.",
    )
    options: Annotated[
        dict[str, Any],
        BeforeValidator(validate_cascader_options),
        Field(
            description="Nested tree: dict keys are branch labels; each branch is a dict or a non-empty list of "
            "scalar leaf values (str, int, float, bool, or date).",
        ),
    ] = {}
    value: Annotated[
        SingleValueType | list[SingleValueType] | list[list[SingleValueType]] | None,
        Field(
            default=None,
            validate_default=True,
            description="Selected value. With full_path=False (default): a leaf value (e.g. `'France'`), or a list "
            "of leaves when multi=True. With full_path=True: a root-to-leaf path (e.g. `['Europe', 'France']`), or "
            "a list of such paths when multi=True. Must be valid for `options`. If omitted, the first "
            "leaf/path is selected.",
        ),
    ]
    multi: bool = Field(default=True, description="Whether to enable selection of multiple values")
    title: str = Field(default="", description="Title to be displayed")
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description.""",
        ),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `vdc.Cascader` and overwrite any
defaults chosen by the Vizro team. This may have unexpected behavior.
Visit the [vdc documentation](https://github.com/mckinsey/vizro/tree/main/vizro-dash-components)
to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
underlying component may change in the future.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _in_container: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(vdc.Cascader().available_properties)

    @model_validator(mode="after")
    def _validate_value(self):
        # Validate `value` against `options` per mode. For a dynamic filter, `options` is empty here at
        # construction and only populated later when its `pre_build` assigns `self.options`; because
        # `validate_assignment=True`, that assignment re-runs this validator, which then validates against the
        # now-populated tree. Leaf mode may normalize `value` (bare multi scalar → list); this is idempotent, so
        # re-runs are safe.
        if not self.options:
            return self

        # `None` and an empty list both mean "no selection".
        no_selection = self.value is None or (isinstance(self.value, list) and not self.value)

        if self.full_path:
            if not no_selection:
                _validate_path_value(self.value, self.options, multi=self.multi)
            return self

        # Leaf mode: collect leaves once (used for both the duplicate check and O(1) membership). Duplicate
        # leaves are forbidden regardless of whether a value is set (they are inherently ambiguous).
        leaves = _iter_cascader_leaves_depth_first(self.options)
        _reject_duplicate_leaves(leaves)
        if not no_selection:
            # Assign via `__dict__` to normalize (e.g. a bare multi scalar → list) without re-triggering
            # `validate_assignment`; idempotent, so re-runs on the canonical value are safe.
            self.__dict__["value"] = _validate_leaf_value(self.value, set(leaves), multi=self.multi)
        return self

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.value"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.value",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.value"}

    def __call__(self, options):
        # Fill the first-leaf/path default when unset (mirrors Dropdown). Otherwise pass the stored value straight
        # through: it is already valid for the mode. We must not re-validate against these `options`, because a
        # runtime data reload can narrow the tree so a still-valid selection is temporarily absent.
        # `self.value` is already canonical for the mode (validated/normalized in `_validate_value`, which also
        # re-runs when a dynamic filter assigns `options` in `pre_build`): a leaf scalar or list of leaves in leaf
        # mode, a path or list of paths in path mode. A default is filled the same way when unset.
        value = (
            get_cascader_default_value(options, multi=self.multi, full_path=self.full_path)
            if self.value is None
            else self.value
        )

        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "options": options,
            "value": value,
            "multi": self.multi,
            "full_path": self.full_path,
            "persistence": True,
            "persistence_type": "session",
            "placeholder": "Select option",
            "clearable": self.multi,  # Set clearable=False only for single-select dropdowns
        }

        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description], html_for=self.id
                )
                if self.title
                else None,
                vdc.Cascader(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            self.value = get_cascader_default_value(self.options, multi=self.multi, full_path=self.full_path)
        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
