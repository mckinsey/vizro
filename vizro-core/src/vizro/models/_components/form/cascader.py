from __future__ import annotations

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
            try:
                TypeAdapter(SingleValueType).validate_python(item)
            except Exception as exc:
                raise ValueError(
                    "Cascader leaf lists must contain only scalar values "
                    "(str, number, bool, or date), not dicts or nested structures."
                ) from exc
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
# collecting leaves in depth-first order) are required elsewhere anyway—`validate_cascader_value` must check
# `value` against the flattened leaves, and `get_cascader_default_value` walks in the same depth-first order
# to resolve the first leaf list (siblings of `leaves[0]`) for multi-select defaults.
def validate_cascader_options_dict(data: Any) -> Any:
    """Ensure options are a nested dict with scalar-only leaf lists; reject root list and empty trees."""
    if not isinstance(data, dict):
        raise ValueError("Cascader options must be a nested dictionary (not a list).")
    if not data:
        raise ValueError("Cascader options cannot be empty.")
    _walk_cascader_branch(data, path="")
    if not _iter_cascader_leaves_depth_first(data):
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


def _first_cascader_leaf_list_depth_first(options: dict[str, Any]) -> list[SingleValueType]:
    """First leaf list encountered in depth-first key order; equals all siblings of `leaves[0]` including `leaves[0]`."""
    for value in options.values():
        if isinstance(value, list):
            return cast(list[SingleValueType], list(value))
        return _first_cascader_leaf_list_depth_first(value)
    raise ValueError("Cascader options must contain at least one leaf value.")


def get_cascader_default_value(options: dict[str, Any], *, multi: bool) -> SingleValueType | MultiValueType:
    first_sibling_group = _first_cascader_leaf_list_depth_first(options)
    if multi:
        return cast(MultiValueType, list(first_sibling_group))
    return first_sibling_group[0]


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
    """Hierarchical single/multi-option selector.

    For use with [`Parameter`][vizro.models.Parameter] only — not supported on [`Filter`][vizro.models.Filter].

    [`set_control`][vizro.actions.set_control] does not treat this selector as categorical yet.

    Abstract: Usage documentation
        [How to use parameters](../user-guides/parameters.md)

    """

    type: Literal["cascader"] = "cascader"
    options: Annotated[dict[str, Any], BeforeValidator(validate_cascader_options_dict)] = {}
    value: Annotated[
        SingleValueType | MultiValueType | None,
        AfterValidator(validate_cascader_value),
        Field(default=None, validate_default=True),
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
    # Unlike dcc.Dropdonw, vdc.Cascader has options as a required field (maybe a mistake).
    _inner_component_properties: list[str] = PrivateAttr(
        vdc.Cascader(options={}).available_properties
    )

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
