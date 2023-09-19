from typing import Dict, List, Literal, Optional

from dash import Input, Output, State, callback, callback_context, dcc, html
from pydantic import Field, validator

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import (
    set_default_marks,
    validate_max,
    validate_slider_value,
    validate_step,
)
from vizro.models._models_utils import _log_call


class Slider(VizroBaseModel):
    """Numeric single-selector `Slider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider).

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[Dict[float, str]]): Marks to be displayed on slider. Defaults to `None`.
        value (Optional[float]): Default value for slider. Defaults to `None`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["slider"] = "slider"
    min: Optional[float] = Field(None, description="Start value for slider.")
    max: Optional[float] = Field(None, description="End value for slider.")
    step: Optional[float] = Field(None, description="Step-size for marks on slider.")
    marks: Optional[Dict[float, str]] = Field(None, description="Marks to be displayed on slider.")
    value: Optional[float] = Field(None, description="Default value for slider.")
    title: Optional[str] = Field(None, description="Title to be displayed.")
    actions: List[Action] = []

    # Re-used validators
    _validate_max = validator("max", allow_reuse=True)(validate_max)
    _validate_value = validator("value", allow_reuse=True)(validate_slider_value)
    _validate_step = validator("step", allow_reuse=True)(validate_step)
    _set_default_marks = validator("marks", allow_reuse=True, always=True)(set_default_marks)
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        output = [
            Output(f"{self.id}_text_value", "value"),
            Output(self.id, "value"),
            Output(f"{self.id}_temp_store", "data"),
        ]
        input = [
            Input(f"{self.id}_text_value", "value"),
            Input(self.id, "value"),
            State(f"{self.id}_temp_store", "data"),
        ]

        @callback(output=output, inputs=input)
        def update_slider_value_callback(start, slider, input_store):
            trigger_id = callback_context.triggered_id
            return self._update_slider_value(trigger_id, start, slider, input_store)

        return html.Div(
            [
                html.P(self.title) if self.title else None,
                html.Div(
                    [
                        dcc.Slider(
                            id=self.id,
                            min=self.min,
                            max=self.max,
                            step=self.step,
                            marks=self.marks,
                            value=self.value or self.min,
                            included=False,
                            persistence=True,
                            className="slider_control" if self.step else "slider_control_no_space",
                        ),
                        dcc.Input(
                            id=f"{self.id}_text_value",
                            type="number",
                            placeholder="end",
                            min=self.min,
                            max=self.max,
                            value=self.value or self.min,
                            persistence=True,
                            className="slider_input_field_right" if self.step else "slider_input_field_no_space_right",
                        ),
                        dcc.Store(id=f"{self.id}_temp_store", storage_type="local"),
                    ],
                    className="slider_inner_container",
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )

    def _update_slider_value(self, trigger_id, start, slider, input_store):
        if trigger_id == f"{self.id}_text_value":
            text_value = start
        elif trigger_id == f"{self.id}":
            text_value = slider
        else:
            text_value = input_store or self.value or self.min
        text_value = min(max(self.min, text_value), self.max)

        return text_value, text_value, text_value
