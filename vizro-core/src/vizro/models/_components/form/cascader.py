from __future__ import annotations

from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
import vizro_dash_components as vdc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, TypeAdapter, ValidationInfo, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    ActionsType,
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
    # Duplicate leaf labels across different branches are allowed: a selection is addressed by its full
    # root-to-leaf path (see `value`), so `["Eu", "Springfield"]` and `["Us", "Springfield"]` are distinct.
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
    """Path key used for membership tests: branch labels compared as `str`, the leaf kept typed.

    Options built from a dataframe stringify branch labels (see `_dataframe_path_to_cascader_options` in
    filter.py) but keep leaves typed, so a numeric branch code like `1` must match the string key `"1"`.
    """
    path = list(path)
    return (*(str(segment) for segment in path[:-1]), path[-1])


# `get_cascader_default_value` uses the paths under the first root key in depth-first order: single-select
# takes the first path; multi-select takes the full list of paths.
def get_cascader_default_value(
    options: dict[str, Any], *, multi: bool
) -> list[SingleValueType] | list[list[SingleValueType]]:
    if not options:
        raise ValueError("Cascader options must be non-empty before a default value can be computed.")
    first_key = next(iter(options))
    first_branch_paths = _iter_cascader_paths_depth_first({first_key: options[first_key]})
    if multi:
        return first_branch_paths
    return first_branch_paths[0]


def _cascader_value_allowed(value: Any, valid_paths: set[tuple[Any, ...]]) -> bool:
    if not value:  # None or [] means nothing is selected, which is always allowed.
        return True
    paths = value if isinstance(value[0], (list, tuple)) else [value]
    return all(_normalize_cascader_path(path) in valid_paths for path in paths if path)


def validate_cascader_value(value: Any, info: ValidationInfo) -> Any:
    if "options" not in info.data or not info.data["options"]:
        return value
    valid_paths = {_normalize_cascader_path(path) for path in _iter_cascader_paths_depth_first(info.data["options"])}
    if value is not None and not _cascader_value_allowed(value, valid_paths):
        raise ValueError("Please provide a valid value from `options`.")
    return value


def validate_cascader_multi(multi: bool, info: ValidationInfo) -> bool:
    """Reject a list of paths when `multi=False`.

    Unlike flat selectors, a single-select Cascader `value` is itself a list (one root-to-leaf path), so a
    list-of-paths (its first element is a list) is what distinguishes a multi value from a single one.
    """
    value = info.data.get("value")
    if not multi and value and isinstance(value[0], (list, tuple)):
        raise ValueError("Please set multi=True if providing a list of paths.")
    return multi


class Cascader(VizroBaseModel):
    """Cascader selector for [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [Hierarchical selectors](user-guides/selectors.md#hierarchical-selectors)

    """

    type: Literal["cascader"] = "cascader"
    options: Annotated[
        dict[str, Any],
        BeforeValidator(validate_cascader_options),
        Field(
            description="Nested tree: dict keys are branch labels; each branch is a dict or a non-empty list of "
            "scalar leaf values (str, int, float, bool, or date).",
        ),
    ] = {}
    value: Annotated[
        list[SingleValueType] | list[list[SingleValueType]] | None,
        AfterValidator(validate_cascader_value),
        Field(
            default=None,
            validate_default=True,
            description="Selected leaf path (the list of node values from the root down to the leaf, e.g. "
            "`['Europe', 'France']`), or a list of such paths when multi=True. Must be valid for `options`. "
            "If omitted, the first leaf path is selected.",
        ),
    ]
    multi: Annotated[
        bool,
        AfterValidator(validate_cascader_multi),
        Field(default=True, description="Whether to allow selection of multiple values", validate_default=True),
    ]
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
        value = self.value
        # `value` is a single path (list of scalars) or a list of paths. Under multi, wrap a lone single
        # path into a list-of-paths; a correctly-shaped list-of-paths (first element is itself a list) and
        # None/[] are left untouched.
        if self.multi and value and not isinstance(value[0], (list, tuple)):
            value = cast("list[list[SingleValueType]]", [value])

        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "options": options,
            "value": value,
            "multi": self.multi,
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
            self.value = get_cascader_default_value(self.options, multi=self.multi)
        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
