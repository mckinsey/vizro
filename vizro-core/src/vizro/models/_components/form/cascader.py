from __future__ import annotations

from collections import Counter
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
import vizro_dash_components as vdc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, TypeAdapter, ValidationInfo, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form.dropdown import validate_multi
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    ActionsType,
    MultiValueType,
    SingleValueType,
    _IdProperty,
)


def _validate_cascader_leaf_scalar(item: Any) -> None:
    try:
        TypeAdapter(SingleValueType).validate_python(item)
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
        for item in node:
            _validate_cascader_leaf_scalar(item)
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
    dup_counts = Counter(leaves)
    if duplicates := [v for v, c in dup_counts.items() if c > 1]:
        raise ValueError(f"Cascader options must not contain duplicate leaf values: {duplicates}.")
    return data


def _iter_cascader_leaves_depth_first(options: dict[str, Any]) -> list[SingleValueType]:
    leaves: list[SingleValueType] = []
    for value in options.values():
        if isinstance(value, list):
            leaves.extend(cast(list[SingleValueType], value))
        else:
            leaves.extend(_iter_cascader_leaves_depth_first(value))
    return leaves


# `get_cascader_default_value` uses leaves under the first root key in depth-first order: single-select takes
# `leaves[0]`; multi-select takes the full list.
def get_cascader_default_value(options: dict[str, Any], *, multi: bool) -> SingleValueType | MultiValueType:
    if not options:
        raise ValueError("Cascader options must be non-empty before a default value can be computed.")
    first_value = next(iter(options.values()))
    if isinstance(first_value, list):
        leaves = cast(list[SingleValueType], list(first_value))
    else:
        leaves = _iter_cascader_leaves_depth_first(first_value)
    if multi:
        return cast(MultiValueType, list(leaves))
    return leaves[0]


def _cascader_value_allowed(value: SingleValueType | MultiValueType, leaves: list[SingleValueType]) -> bool:
    if isinstance(value, list):
        return all(item in leaves for item in value)
    return value in leaves


def validate_cascader_value(value: Any, info: ValidationInfo) -> Any:
    if "options" not in info.data or not info.data["options"]:
        return value
    leaves = _iter_cascader_leaves_depth_first(info.data["options"])
    if value is not None and not _cascader_value_allowed(value, leaves):
        raise ValueError("Please provide a valid value from `options`.")
    return value


class Cascader(VizroBaseModel):
    """Cascader selector for [`Parameter`][vizro.models.Parameter] and [`Filter`][vizro.models.Filter].

    Abstract: Usage documentation
        [Hierarchical selectors](../user-guides/selectors.md#hierarchical-selectors)

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
        SingleValueType | MultiValueType | None,
        AfterValidator(validate_cascader_value),
        Field(
            default=None,
            validate_default=True,
            description="Selected leaf value, or list of leaves when multi=True. Must be valid for `options`. "
            "If omitted, the first parent node is selected.",
        ),
    ]
    multi: Annotated[
        bool,
        AfterValidator(validate_multi),
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

    _in_container: bool = PrivateAttr(False)
    # Unlike dcc.Dropdown, vdc.Cascader has options as a required field (maybe a mistake).
    _inner_component_properties: list[str] = PrivateAttr(vdc.Cascader(options={}).available_properties)

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

    @_log_call
    def build(self):
        value = self.value
        if self.multi and value is not None and not isinstance(value, list):
            value = cast(MultiValueType, [value])

        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "options": self.options,
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
