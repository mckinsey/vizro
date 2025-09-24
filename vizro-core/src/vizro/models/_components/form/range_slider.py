from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, conlist, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import (
    set_default_marks,
    validate_max,
    validate_range_value,
    validate_step,
)
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


class RangeSlider(VizroBaseModel):
    """Numeric multi-option selector `RangeSlider`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use numerical selectors](../user-guides/selectors.md/#numerical-selectors)

    Args:
        type (Literal["range_slider"]): Defaults to `"range_slider"`.
        min (Optional[float]): Start value for slider. Defaults to `None`.
        max (Optional[float]): End value for slider. Defaults to `None`.
        step (Optional[float]): Step-size for marks on slider. Defaults to `None`.
        marks (Optional[dict[Union[float, int], str]]): Marks to be displayed on slider. Defaults to `{}`.
        value (Optional[list[float]]): Default start and end value for slider. Must be 2 items. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dcc.RangeSlider` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/rangeslider)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["range_slider"] = "range_slider"
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
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for value field
    value: Optional[  # type: ignore[valid-type]
        Annotated[
            conlist(float, min_length=2, max_length=2),
            AfterValidator(validate_range_value),
        ]
    ] = Field(default=None)
    title: str = Field(default="", description="Title to be displayed.")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dcc.RangeSlider` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/rangeslider)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dcc.RangeSlider().available_properties)

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

    def __call__(self, min, max):
        output = [
            Output(self.id, "value", allow_duplicate=True),
            Output(f"{self.id}_start_value", "value"),
            Output(f"{self.id}_end_value", "value"),
        ]
        inputs = [
            Input(self.id, "value"),
            Input(f"{self.id}_start_value", "value"),
            Input(f"{self.id}_end_value", "value"),
            State(self.id, "id"),
        ]

        clientside_callback(
            ClientsideFunction(namespace="range_slider", function_name="update_range_slider_values"),
            output=output,
            inputs=inputs,
            prevent_initial_call=True,
        )

        current_value = self.value or [min, max]

        defaults = {
            "id": self.id,
            "min": min,
            "max": max,
            "step": self.step,
            "marks": self.marks,
            "value": current_value,
            "persistence": True,
            "persistence_type": "session",
            "className": "slider-track-without-marks" if self.marks is None else "slider-track-with-marks",
        }

        description = self.description.build().children if self.description else [None]
        return html.Div(
            children=[
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
                                    id=f"{self.id}_start_value",
                                    type="number",
                                    placeholder="min",
                                    min=min,
                                    max=max,
                                    step=self.step,
                                    value=current_value[0],
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                                html.Span("-", className="slider-text-input-range-separator"),
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type="number",
                                    placeholder="max",
                                    min=min,
                                    max=max,
                                    step=self.step,
                                    value=current_value[1],
                                    persistence=True,
                                    persistence_type="session",
                                    className="slider-text-input-field",
                                ),
                            ],
                            className="slider-text-input-container",
                        ),
                    ],
                    className="slider-label-input",
                ),
                dcc.RangeSlider(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        if not self.value:
            self.value = [self.min, self.max]

        return self.__call__(self.min, self.max)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.min, self.max)
