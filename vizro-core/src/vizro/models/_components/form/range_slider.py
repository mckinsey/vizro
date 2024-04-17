from typing import Any, Dict, List, Literal, Optional, Union

from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import dash_bootstrap_components as dbc

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import (
    set_default_marks,
    validate_max,
    validate_range_value,
    validate_step,
)
from vizro.models._models_utils import _log_call


class RangeSlider(VizroBaseModel):
    """Numeric multi-option selector `RangeSlider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider).

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[Dict[int, Union[str, dict]]]): Marks to be displayed on slider. Defaults to `{}`.
        value (Optional[List[float]]): Default start and end value for slider. Must be 2 items. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["range_slider"] = "range_slider"
    min: Optional[float] = Field(None, description="Start value for slider.")
    max: Optional[float] = Field(None, description="End value for slider.")
    step: Optional[float] = Field(None, description="Step-size for marks on slider.")
    marks: Optional[Dict[int, Union[str, Dict[str, Any]]]] = Field({}, description="Marks to be displayed on slider.")
    value: Optional[List[float]] = Field(
        None, description="Default start and end value for slider", min_items=2, max_items=2
    )
    title: str = Field("", description="Title to be displayed.")
    actions: List[Action] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Re-used validators
    _validate_max = validator("max", allow_reuse=True)(validate_max)
    _validate_value = validator("value", allow_reuse=True)(validate_range_value)
    _validate_step = validator("step", allow_reuse=True)(validate_step)
    _set_default_marks = validator("marks", allow_reuse=True, always=True)(set_default_marks)
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        init_value = self.value or [self.min, self.max]  # type: ignore[list-item]

        output = [
            Output(f"{self.id}_start_value", "value"),
            Output(f"{self.id}_end_value", "value"),
            Output(self.id, "value"),
            Output(f"{self.id}_input_store", "data"),
        ]
        inputs = [
            Input(f"{self.id}_start_value", "value"),
            Input(f"{self.id}_end_value", "value"),
            Input(self.id, "value"),
            State(f"{self.id}_input_store", "data"),
            State(f"{self.id}_callback_data", "data"),
        ]

        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_range_slider_values"),
            output=output,
            inputs=inputs,
        )

        return html.Div(
            [
                dcc.Store(f"{self.id}_callback_data", data={"id": self.id, "min": self.min, "max": self.max}),
                html.Div(
                    [
                        dbc.Label(self.title, html_for=self.id) if self.title else None,
                        html.Div(
                            [
                                dcc.Input(
                                    id=f"{self.id}_start_value",
                                    type="number",
                                    placeholder="min",
                                    min=self.min,
                                    max=self.max,
                                    step=self.step,
                                    value=init_value[0],
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                                html.Span("-", className="slider-text-input-range-separator"),
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type="number",
                                    placeholder="max",
                                    min=self.min,
                                    max=self.max,
                                    step=self.step,
                                    value=init_value[1],
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                                dcc.Store(id=f"{self.id}_input_store", storage_type="session", data=init_value),
                            ],
                            className="slider-text-input-container",
                        ),
                    ],
                    className="slider-label-input",
                ),
                dcc.RangeSlider(
                    id=self.id,
                    min=self.min,
                    max=self.max,
                    step=self.step,
                    marks=self.marks,
                    value=init_value,
                    persistence=True,
                    persistence_type="session",
                    className="slider-track-without-marks" if self.marks is None else "slider-track-with-marks",
                ),
            ],
            className="input-container",
            id=f"{self.id}_outer",
        )
