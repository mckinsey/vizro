from datetime import datetime, time
from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import validate_time_picker_range
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


def _coerce_to_time(v: Any) -> Any:
    # pd.Timestamp is a subclass of datetime, so this handles both
    if isinstance(v, datetime):
        return v.time()
    return v


def _time_to_str(t: time | None) -> str | None:
    if t is None:
        return None
    return t.strftime("%H:%M:%S")


class TimePicker(VizroBaseModel):
    """Temporal time-of-day single/range option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].
    """

    type: Literal["time_picker"] = "time_picker"
    value: Annotated[
        list[time] | time | None,
        Field(default=None, description="Default time/times for time picker."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    range: Annotated[
        bool,
        AfterValidator(validate_time_picker_range),
        Field(default=True, description="Boolean flag for displaying range picker.", validate_default=True),
    ]
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
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
                description="""Extra keyword arguments passed to `dmc.TimePicker` and overwrite
any defaults chosen by the Vizro team.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dmc.TimePicker().available_properties)
    _callback_registered: bool = PrivateAttr(False)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.{'data' if self.range else 'value'}"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        prop = "data" if self.range else "value"
        return {
            "__default__": f"{self.id}.{prop}",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        prop = "data" if self.range else "value"
        return {"__default__": f"{self.id}.{prop}"}

    @_log_call
    def build(self):
        value_start = _time_to_str(self.value[0]) if isinstance(self.value, list) else None
        value_end = _time_to_str(self.value[1]) if isinstance(self.value, list) else None
        value_single = _time_to_str(self.value) if isinstance(self.value, time) else None

        description = self.description.build().children if self.description else [None]
        label = (
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                html_for=self.id,
            )
            if self.title
            else None
        )

        defaults = {"withSeconds": True, "debounce": True}
        if self.range:
            if not self._callback_registered:
                clientside_callback(
                    ClientsideFunction(namespace="time_picker", function_name="update_time_picker_store"),
                    output=[
                        Output(self.id, "data"),
                        Output(f"{self.id}-start", "value"),
                        Output(f"{self.id}-end", "value"),
                    ],
                    inputs=[
                        Input(self.id, "data"),
                        Input(f"{self.id}-start", "value"),
                        Input(f"{self.id}-end", "value"),
                        State(self.id, "id"),
                    ],
                    hidden=True,
                )
                self._callback_registered = True

            start_defaults = {"id": f"{self.id}-start", "value": value_start, **defaults}
            end_defaults = {"id": f"{self.id}-end", "value":value_end, **defaults}
            return html.Div(
                children=[
                    label,
                    html.Div(
                        children=[
                            dmc.TimePicker(**(start_defaults | self.extra)),
                            dmc.TimePicker(**(end_defaults | self.extra)),
                        ],
                        style={"display": "flex", "gap": "8px"},
                    ),
                    dcc.Store(id=self.id, data=[value_start, value_end], storage_type="session"),
                ]
            )
        else:
            defaults = {"id": self.id, "value": value_single, **defaults}
            return html.Div(
                children=[
                    label,
                    dmc.TimePicker(**(defaults | self.extra)),
                ]
            )