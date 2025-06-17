from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr
from pydantic.functional_serializers import PlainSerializer
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import (
    set_default_marks,
    validate_max,
    validate_range_value,
    validate_step,
)
from vizro.models._models_utils import _log_call
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionType, _IdProperty


class Slider(VizroBaseModel):
    """Numeric single-option selector `Slider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[dict[Union[float, int], str]]): Marks to be displayed on slider. Defaults to `{}`.
        value (Optional[float]): Default value for slider. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dcc.Slider` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/slider)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["slider"] = "slider"
    min: Optional[float] = Field(default=None, description="Start value for slider.")
    max: Annotated[
        Optional[float], AfterValidator(validate_max), Field(default=None, description="End value for slider.")
    ]
    step: Annotated[
        Optional[float],
        AfterValidator(validate_step),
        Field(default=None, description="Step-size for marks on slider."),
    ]
    marks: Annotated[
        Optional[dict[float, str]],
        AfterValidator(set_default_marks),
        Field(default={}, description="Marks to be displayed on slider.", validate_default=True),
    ]
    value: Annotated[
        Optional[float],
        AfterValidator(validate_range_value),
        Field(default=None, description="Default value for slider."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dcc.Slider` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/slider)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)

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

    def __call__(self, min, max, current_value):
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
        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "min": min,
            "max": max,
            "step": self.step,
            "marks": self.marks,
            "value": current_value,
            "included": False,
            "persistence": True,
            "persistence_type": "session",
            "className": "slider-track-without-marks" if self.marks is None else "slider-track-with-marks",
        }

        return html.Div(
            children=[
                dcc.Store(f"{self.id}_callback_data", data={"id": self.id, "min": min, "max": max}),
                html.Div(
                    children=[
                        dbc.Label(
                            children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                            html_for=self.id,
                        )
                        if self.title
                        else None,
                        html.Div(
                            [
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type="number",
                                    placeholder="max",
                                    min=min,
                                    max=max,
                                    step=self.step,
                                    value=current_value,
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                                dcc.Store(id=f"{self.id}_input_store", storage_type="session"),
                            ],
                            className="slider-text-input-container",
                        ),
                    ],
                    className="slider-label-input",
                ),
                dcc.Slider(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self, current_value):
        return self.__call__(self.min, self.max, current_value)

    @_log_call
    def build(self):
        current_value = self.value if self.value is not None else self.min
        return (
            self._build_dynamic_placeholder(current_value)
            if self._dynamic
            else self.__call__(self.min, self.max, current_value)
        )
