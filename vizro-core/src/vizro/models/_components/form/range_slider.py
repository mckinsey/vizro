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


class RangeSlider(VizroBaseModel):
    """Numeric multi-selector `RangeSlider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider).

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[Dict[float, str]]): Marks to be displayed on slider. Defaults to `None`.
        value (Optional[List[float]]): Default start and end value for slider. Must be 2 items. Defaults to `None`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["range_slider"] = "range_slider"
    min: Optional[float] = Field(None, description="Start value for slider.")
    max: Optional[float] = Field(None, description="End value for slider.")
    step: Optional[float] = Field(None, description="Step-size for marks on slider.")
    marks: Optional[Dict[float, str]] = Field(None, description="Marks to be displayed on slider.")
    value: Optional[List[float]] = Field(
        None, description="Default start and end value for slider", min_items=2, max_items=2
    )
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
        value = self.value or [self.min, self.max]  # type: ignore[list-item]

        output = [
            Output(f"{self.id}_start_value", "value"),
            Output(f"{self.id}_end_value", "value"),
            Output(self.id, "value"),
            Output(f"temp-store-range_slider-{self.id}", "data"),
        ]
        input = [
            Input(f"{self.id}_start_value", "value"),
            Input(f"{self.id}_end_value", "value"),
            Input(self.id, "value"),
            State(f"temp-store-range_slider-{self.id}", "data"),
        ]

        @callback(output=output, inputs=input)
        def update_slider_values_callback(start, end, slider, input_store):
            trigger_id = callback_context.triggered_id

            return self._update_slider_values(
                start_txt=start, end_txt=end, slider=slider, input_store=input_store, value=value, trigger_id=trigger_id
            )

        return html.Div(
            [
                html.P(self.title) if self.title else None,
                html.Div(
                    [
                        dcc.RangeSlider(
                            id=self.id,
                            min=self.min,
                            max=self.max,
                            step=self.step,
                            marks=self.marks,
                            value=value,
                            persistence=True,
                            className="range_slider_control" if self.step else "range_slider_control_no_space",
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id=f"{self.id}_start_value",
                                    type="number",
                                    placeholder="start",
                                    min=self.min,
                                    max=self.max,
                                    value=value[0],
                                    size="24px",
                                    persistence=True,
                                    className="slider_input_field_left"
                                    if self.step
                                    else "slider_input_field_no_space_left",
                                ),
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type="number",
                                    placeholder="end",
                                    min=self.min,
                                    max=self.max,
                                    value=value[1],
                                    persistence=True,
                                    className="slider_input_field_right"
                                    if self.step
                                    else "slider_input_field_no_space_right",
                                ),
                                dcc.Store(id=f"temp-store-range_slider-{self.id}", storage_type="local"),
                            ],
                            className="slider_input_container",
                        ),
                    ],
                    className="range_slider_inner_container",
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )

    def _update_slider_values(self, trigger_id, start_txt, end_txt, slider, input_store, value):  # noqa: PLR0913
        if trigger_id == f"{self.id}_start_value" or trigger_id == f"{self.id}_end_value":
            start_text_value, end_text_value = start_txt, end_txt
        elif trigger_id == self.id:
            start_text_value, end_text_value = slider
        else:
            start_text_value, end_text_value = input_store if input_store is not None else value

        start_value = min(start_text_value, end_text_value)
        end_value = max(start_text_value, end_text_value)

        start_value = max(self.min, start_value)
        end_value = min(self.max, end_value)
        slider_value = [start_value, end_value]

        return start_value, end_value, slider_value, (start_value, end_value)
