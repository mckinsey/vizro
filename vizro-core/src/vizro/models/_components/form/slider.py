from typing import Literal, Optional

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


class Slider(VizroBaseModel):
    """Numeric single-option selector `Slider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider).

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[dict[int, Union[str, dict]]]): Marks to be displayed on slider. Defaults to `{}`.
        value (Optional[float]): Default value for slider. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["slider"] = "slider"
    min: Optional[float] = Field(None, description="Start value for slider.")
    max: Optional[float] = Field(None, description="End value for slider.")
    step: Optional[float] = Field(None, description="Step-size for marks on slider.")
    marks: Optional[dict[float, str]] = Field({}, description="Marks to be displayed on slider.")
    value: Optional[float] = Field(None, description="Default value for slider.")
    title: str = Field("", description="Title to be displayed.")
    actions: list[Action] = []

    _dynamic: bool = PrivateAttr(False)

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Re-used validators
    _validate_max = validator("max", allow_reuse=True)(validate_max)
    _validate_value = validator("value", allow_reuse=True)(validate_range_value)
    _validate_step = validator("step", allow_reuse=True)(validate_step)
    _set_default_marks = validator("marks", allow_reuse=True, always=True)(set_default_marks)
    _set_actions = _action_validator_factory("value")

    def __call__(self, current_value=None, new_min=None, new_max=None, **kwargs):
        return self._build_static(current_value=current_value, new_min=new_min, new_max=new_max, **kwargs)

    def _build_static(self, is_dynamic_build=False, current_value=None, new_min=None, new_max=None, **kwargs):
        _min = new_min if new_min else self.min
        _max = new_max if new_max else self.max
        init_value = current_value or self.value or _min

        output = [
            Output(f"{self.id}_end_value", "value"),
            Output(self.id, "value"),
            Output(f"{self.id}_input_store", "data"),
        ]
        inputs = [
            Input(f"{self.id}_end_value", "value"),
            Input(self.id, "value"),
            State(f"{self.id}_input_store", "data"),
            State(f"{self.id}_callback_data", "data"),
        ]

        clientside_callback(
            ClientsideFunction(namespace="slider", function_name="update_slider_values"),
            output=output,
            inputs=inputs,
        )

        # TODO - TLDR:
        #  if static: -> assign init_value to the dcc.Store
        #  if dynamic:
        #    if dynamic_build: -> dcc.Store(id=f"{self.id}_input_store",  storage_type="session", data=None)
        #    if static_build: -> dcc.Store(id=f"{self.id}_input_store",  storage_type="session") + on_page_load_value
        #      to UI components like dcc.Slider and dcc.Input. on_page_load_value is propagated from the OPL()
        #  + changes on the slider.js so it returns value if is dynamic build and raises no_update of it's static_build.

        # How-it-works?:
        #   1. If it's a static component:
        #     0. Build method is only called once - in the page.build(), so before the OPL().
        #     1. Return always dcc.Store(data=init_value) -> the persistence will work here.
        #     2. Make client_side callback that maps stored value to the one or many UI components.
        #       -> This callback is triggered before OPL and it ensures that the correct value is propagated to the OPL
        #     3. Outcome: persistence storage keeps only dcc.store value. UI components are always correctly selected.
        #   2. If it's a dynamic compoenent:
        #     Build method is called twice - from the page.build() and from the OPL()
        #       1. page.build():
        #         1. page_build() is _build_dynamic and it returns dcc.Store(data=None) - "none" is immediatelly
        #           overwritten with the persited value if it exists. Otherwise it's overwritten with self.value or min.
        #         2. Make client_side callback that maps stored value to the one or many UI components.
        #           -> This callback is triggered before OPL and ensures that the correct value is propagated to the OPL
        #       2. OPL():
        #         1. OPL propagates currently selected value (e.g. slider value) to _build_static()
        #         2. build static returns dcc.Store(). But it returns slider and other compoents with the slider_value
        #           propagated from the OPL.
        #         3. clienside_callback is triggered again but as all input values are the same it raises
        #           dash_clienside.no_update and the process is done. Otherwise, filter_action would be triggered

        stop = 0

        return html.Div(
            children=[
                dcc.Store(f"{self.id}_callback_data", data={"id": self.id, "min": _min, "max": _max, "is_dynamic_build": is_dynamic_build}),
                html.Div(
                    children=[
                        dbc.Label(children=self.title, html_for=self.id) if self.title else None,
                        html.Div(
                            [
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type="number",
                                    placeholder="max",
                                    min=_min,
                                    max=_max,
                                    step=self.step,
                                    value=init_value,
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                                dcc.Store(id=f"{self.id}_input_store",  storage_type="session", data=init_value)
                                if is_dynamic_build
                                else dcc.Store(id=f"{self.id}_input_store", storage_type="session"),
                            ],
                            className="slider-text-input-container",
                        ),
                    ],
                    className="slider-label-input",
                ),
                dcc.Slider(
                    id=self.id,
                    min=_min,
                    max=_max,
                    step=self.step,
                    marks=self.marks,
                    value=init_value,
                    included=False,
                    persistence=True,
                    persistence_type="session",
                    className="slider-track-without-marks" if self.marks is None else "slider-track-with-marks",
                ),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            self.value = self.min

        return self._build_static(is_dynamic_build=True)

    @_log_call
    def build(self):
        # TODO: We don't have to implement _build_dynamic_placeholder, _build_static here. It's possible to:
        #  if dynamic and self.value is None -> set self.value + return standard build (static)
        return self._build_dynamic_placeholder() if self._dynamic else self._build_static()
