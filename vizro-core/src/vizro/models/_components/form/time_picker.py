from datetime import datetime, time
from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import validate_range_picker
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


def _coerce_to_time(value: Any) -> Any:
    """Coerce datetime to time object."""
    if isinstance(value, datetime):
        return value.time()
    return value


class TimePicker(VizroBaseModel):
    """Temporal time-of-day single/range option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].
    """

    type: Literal["time_picker"] = "time_picker"
    value: Annotated[
        # Accept strings as-is so input value can stay in "HH:MM" format. Using only `datetime.time` would coerce them
        # to "HH:MM:SS", which breaks initial-load filtering because the filter does not strip seconds.
        list[time | str] | time | str | None,
        Field(default=None, description="Default time/times for time picker."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    range: Annotated[
        bool,
        AfterValidator(validate_range_picker),
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

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.{'data' if self.range else 'value'}"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.{"data" if self.range else "value"}",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.{"data" if self.range else "value"}"}

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]
        label = (
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                html_for=self.id,
            )
            if self.title
            else None
        )

        defaults: dict[str, Any] = {"debounce": True}
        if self.range:
            # Add the clientside callback only for range TimePicker
            self._update_range_time_picker_store()

            _value = [None, None] if self.value is None else self.value
            start_defaults = {"id": f"{self.id}-start", "value": _value[0], **defaults}
            end_defaults = {"id": f"{self.id}-end", "value": _value[1], **defaults}

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
                    dcc.Store(id=self.id, data=_value, storage_type="session"),
                ]
            )
        else:
            defaults = {"id": self.id, "value": self.value, **defaults}
            return html.Div(
                children=[
                    label,
                    dmc.TimePicker(**(defaults | self.extra)),
                ]
            )

    def _update_range_time_picker_store(self):
        """Define the clientside callback responsible for syncing the range time picker store."""
        clientside_callback(
            ClientsideFunction(namespace="time_picker", function_name="update_range_time_picker_store"),
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
