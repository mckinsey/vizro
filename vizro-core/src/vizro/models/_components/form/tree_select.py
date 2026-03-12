from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
import feffery_antd_components as fac
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, ValidationInfo, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, MultiValueType, SingleValueType, TreeOptionsType, _IdProperty


def _validate_options_structure(options: Any) -> None:
    """Recursively validate that options is a dict of str -> list[str] | dict."""
    if not isinstance(options, dict):
        raise ValueError("options must be a dict.")
    for key, value in options.items():
        if not isinstance(key, str):
            raise ValueError(f"options keys must be strings, got {type(key)}")
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, str):
                    raise ValueError(f"Leaf values must be strings, got {type(item)}: {item!r}")
        elif isinstance(value, dict):
            _validate_options_structure(value)
        else:
            raise ValueError(
                f"options values must be list[str] or dict, got {type(value)} for key {key!r}"
            )


def _convert_options(d: dict | list) -> list[dict]:
    """Convert nested dict options to AntdTreeSelect treeData format."""
    if isinstance(d, list):
        return [{"title": v, "key": v, "value": v} for v in d]
    return [
        {"title": k, "key": k, "value": k, "children": _convert_options(v)}
        for k, v in d.items()
    ]


def _extract_leaf_keys(d: dict | list) -> set[str]:
    """Recursively collect all leaf string values from the nested dict."""
    if isinstance(d, list):
        return set(d)
    keys: set[str] = set()
    for v in d.values():
        keys |= _extract_leaf_keys(v)
    return keys


def _validate_multi(multi: bool, info: ValidationInfo) -> bool:
    if "value" not in info.data:
        return multi
    if info.data["value"] and multi is False and isinstance(info.data["value"], list):
        raise ValueError("Please set multi=True if providing a list of default values.")
    return multi


def _validate_tree_value(value, info: ValidationInfo):
    if "options" not in info.data or not info.data["options"]:
        return value
    leaf_keys = _extract_leaf_keys(info.data["options"])
    if value and not (
        all(v in leaf_keys for v in value) if isinstance(value, list) else value in leaf_keys
    ):
        raise ValueError("Please provide a valid value from `options`.")
    return value


class TreeSelect(VizroBaseModel):
    """Hierarchical multi/single-option selector.

    Can be provided to [`Parameter`][vizro.models.Parameter].

    """

    type: Literal["tree_select"] = "tree_select"
    options: TreeOptionsType
    value: Annotated[
        SingleValueType | MultiValueType | None,
        AfterValidator(_validate_tree_value),
        Field(default=None, validate_default=True),
    ]
    multi: Annotated[
        bool,
        AfterValidator(_validate_multi),
        Field(default=True, validate_default=True),
    ]
    title: str = Field(default="", description="Title to be displayed")
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        Field(default=None),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments passed to `fac.AntdTreeSelect` and overwrite any
defaults chosen by the Vizro team. This may have unexpected behavior.""",
            ),
        ]
    ]

    @model_validator(mode="before")
    @classmethod
    def _validate_options_structure(cls, data: Any) -> Any:
        if "options" in data and isinstance(data["options"], dict):
            _validate_options_structure(data["options"])
        return data

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

    def __call__(self):
        tree_data = _convert_options(self.options)
        value = self.value if self.value is not None else ([] if self.multi else None)
        description = self.description.build().children if self.description else [None]

        defaults = {
            "id": self.id,
            "treeData": tree_data,
            "value": value,
            "treeCheckable": self.multi,
            "multiple": self.multi,
            "allowClear": self.multi,
            **( {"showCheckedStrategy": "show-child", "maxTagCount": "responsive"} if self.multi else {} ),
            "listHeight": 300,
            "locale": "en-us",
            "persistence": True,
            "persistence_type": "session",
            "placeholder": "Select option",
        }

        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                    html_for=self.id,
                )
                if self.title
                else None,
                fac.AntdTreeSelect(**(defaults | self.extra)),
            ]
        )

    @_log_call
    def build(self):
        return self.__call__()
