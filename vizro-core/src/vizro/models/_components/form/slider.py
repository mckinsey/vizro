from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, JsonValue, PrivateAttr, conlist, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import (
    to_int_if_whole,
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

# dcc.Slider and dcc.RangeSlider expose different sets of forwardable properties (RangeSlider adds count, allowCross,
# pushable). Compute each once at import rather than reconstructing a throwaway component on every model validation.
_SLIDER_PROPERTIES = dcc.Slider().available_properties
_RANGE_SLIDER_PROPERTIES = dcc.RangeSlider().available_properties


class Slider(VizroBaseModel):
    """Numeric single-option or range selector.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Set `range=True` for a two-handle range selector.

    Abstract: Usage documentation
        [How to use numerical selectors](../user-guides/selectors.md#numerical-selectors)

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
        Field(default={}, description="Marks to be displayed on slider.", validate_default=True),
    ]
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for value field
    value: Annotated[  # type: ignore[valid-type]
        float | conlist(float, min_length=2, max_length=2) | None,
        AfterValidator(validate_range_value),
        Field(
            default=None,
            description="Default value: a single number, or a `[start, end]` pair when `range=True`.",
        ),
    ]
    range: bool = Field(
        default=False,
        description="Whether to display a two-handle range slider. When True, `value` is a `[start, end]` pair.",
    )
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
                description="""Extra keyword arguments that are passed to `dcc.Slider` (or `dcc.RangeSlider` when
`range=True`) and overwrite any defaults chosen by the Vizro team. This may have unexpected behavior.
Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/slider)
to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
underlying component may change in the future.""",
            ),
        ]
    ]

    _dynamic: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(_SLIDER_PROPERTIES)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @model_validator(mode="before")
    @classmethod
    def _validate_range_value_shape(cls, data):
        # `value`'s shape must match `range`: a bare number when range=False, a `[start, end]` list when range=True.
        # Run in "before" mode (not "after") so that under validate_assignment=True the check raises *before* Pydantic
        # writes the field, leaving the model unchanged on a rejected assignment; an "after" validator raises only once
        # the invalid value has already been assigned. "before" also sees both fields on any single-field assignment,
        # so a mismatch is caught whether `value` or `range` is the one reassigned.
        if not isinstance(data, dict):
            return data
        # Subclasses that lock `range` (e.g. RangeSlider fixes range=True) narrow `value` at the field level, which
        # gives a clearer error than this cross-field message, so skip the check for them.
        if cls.model_fields["range"].annotation is not bool:
            return data
        range_ = data.get("range", cls.model_fields["range"].get_default())
        value = data.get("value")
        if range_ and value is not None and not isinstance(value, list):
            raise ValueError("Please set range=False if providing a single value.")
        if not range_ and isinstance(value, list):
            raise ValueError("Please set range=True if providing a list of values.")
        return data

    @model_validator(mode="after")
    def _set_inner_component_properties(self):
        # In range mode the underlying component is dcc.RangeSlider, which exposes extra properties
        # (count, allowCross, pushable) that should be forwardable via `extra` and dynamic updates.
        self._inner_component_properties = _RANGE_SLIDER_PROPERTIES if self.range else _SLIDER_PROPERTIES
        return self

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

    @staticmethod
    def _get_value_from_trigger(value: JsonValue, trigger: JsonValue) -> JsonValue:
        """Return the given `trigger` without modification."""
        return trigger

    def __call__(self, min, max):
        # Overwrite default marks with min and max boundary marks if marks are not provided.
        marks = self.marks if self.marks != {} else {min: str(to_int_if_whole(min)), max: str(to_int_if_whole(max))}

        # In range mode the underlying component is dcc.RangeSlider and the value is a [start, end] pair.
        slider_class = dcc.RangeSlider if self.range else dcc.Slider
        default_value = (self.value or [min, max]) if self.range else (self.value if self.value is not None else min)

        defaults = {
            "id": self.id,
            "min": min,
            "max": max,
            # Only include `step` when defined. Passing None prevents the slider from displaying input values.
            **({"step": self.step} if self.step is not None else {}),
            "marks": marks,
            "value": default_value,
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
                slider_class(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            self.value = [self.min, self.max] if self.range else self.min

        return self.__call__(self.min, self.max)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.min, self.max)
