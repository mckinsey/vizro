from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, model_validator
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


class Slider(VizroBaseModel):
    """Numeric single-option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use numerical selectors](../user-guides/selectors.md/#numerical-selectors)

    """

    type: Literal["slider"] = "slider"
    min: float | None = Field(default=None, description="Start value for slider.")
    max: Annotated[float | None, AfterValidator(validate_max), Field(default=None, description="End value for slider.")]
    step: Annotated[
        float | None,
        AfterValidator(validate_step),
        Field(default=None, description="Step-size for marks on slider."),
    ]
    marks: Annotated[
        dict[float, str] | None,
        AfterValidator(set_default_marks),
        Field(default={}, description="Marks to be displayed on slider.", validate_default=True),
    ]
    value: Annotated[
        float | None,
        AfterValidator(validate_range_value),
        Field(default=None, description="Default value for slider."),
    ]
    title: str = Field(default="", description="Title to be displayed.")
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
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
                description="""Extra keyword arguments that are passed to `dcc.Slider` and overwrite any
defaults chosen by the Vizro team. This may have unexpected behavior.
Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/slider)
to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
underlying component may change in the future.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dcc.Slider().available_properties)

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
        current_value = self.value if self.value is not None else min

        defaults = {
            "id": self.id,
            "min": min,
            "max": max,
            # Only include `step` when defined. Passing None prevents dcc.Slider from displaying input values.
            **({"step": self.step} if self.step is not None else {}),
            "marks": self.marks,
            "value": current_value,
            "persistence": True,
            "persistence_type": "session",
            "dots": True,
        }

        description = self.description.build().children if self.description else [None]
        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                    html_for=self.id,
                )
                if self.title
                else None,
                dcc.Slider(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            self.value = self.min

        return self.__call__(self.min, self.max)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.min, self.max)
