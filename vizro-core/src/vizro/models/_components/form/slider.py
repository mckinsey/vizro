from typing import Dict, List, Literal, Optional

from dash import Input, Output, State, callback, callback_context, dcc, html
from pydantic import Field, validator

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
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
        marks (Optional[Dict[str, float]]): Marks to be displayed on slider. Defaults to `None`.
        value (Optional[float]): Default value for slider. Defaults to `None`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["slider"] = "slider"
    min: Optional[float] = Field(None, description="Start value for slider.")
    max: Optional[float] = Field(None, description="End value for slider.")
    step: Optional[float] = Field(None, description="Step-size for marks on slider.")
    marks: Optional[Dict[str, float]] = Field(None, description="Marks to be displayed on slider.")
    value: Optional[float] = Field(None, description="Default value for slider.")
    title: Optional[str] = Field(None, description="Title to be displayed.")
    actions: List[Action] = []

    # Re-used validators
    _set_actions = _action_validator_factory("value")

    @validator("marks", always=True)
    def set_default_marks(cls, v, values):
        return v if values["step"] is None else {}

    @_log_call
    def build(self):
        output = [
            Output(f"{self.id}_text_value", "value"),
            Output(self.id, "value"),
            Output(f"temp-store-slider-{self.id}", "data"),
        ]
        input = [
            Input(f"{self.id}_text_value", "value"),
            Input(self.id, "value"),
            State(f"temp-store-slider-{self.id}", "data"),
        ]

        @callback(output=output, inputs=input)
        def update_slider_value(start, slider, input_store):
            trigger_id = callback_context.triggered_id
            if trigger_id == f"{self.id}_text_value":
                text_value = start
            elif trigger_id == f"{self.id}":
                text_value = slider
            else:
                text_value = input_store or self.value or self.min
            text_value = min(max(self.min, text_value), self.max)

            return text_value, text_value, text_value

        return html.Div(
            [
                html.P(self.title, id="slider_title") if self.title else None,
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
                            className="slider_input_field_right" if self.step else "slider_input_field_no_space_right",
                            value=self.value or self.min,
                            persistence=True,
                        ),
                        dcc.Store(id=f"temp-store-slider-{self.id}", storage_type="local"),
                    ],
                    className="slider_inner_container",
                ),
            ],
            className="selector_container",
        )
