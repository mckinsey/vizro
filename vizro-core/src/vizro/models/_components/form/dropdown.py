from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, ValidationInfo, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components.form._form_utils import (
    get_dict_options_and_default,
    validate_options_dict,
    validate_value,
)
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    ActionsType,
    MultiValueType,
    OptionsType,
    SingleValueType,
    _IdProperty,
)


def validate_multi(multi, info: ValidationInfo):
    if "value" not in info.data:
        return multi

    if info.data["value"] and multi is False and isinstance(info.data["value"], list):
        raise ValueError("Please set multi=True if providing a list of default values.")
    return multi


class Dropdown(VizroBaseModel):
    """Categorical single/multi-option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use categorical selectors](../user-guides/selectors.md#categorical-selectors)

    """

    type: Literal["dropdown"] = "dropdown"
    options: OptionsType = []
    value: Annotated[
        SingleValueType | MultiValueType | None,
        AfterValidator(validate_value),
        Field(default=None, validate_default=True),
    ]
    multi: Annotated[
        bool,
        AfterValidator(validate_multi),
        Field(default=True, description="Whether to allow selection of multiple values", validate_default=True),
    ]
    title: str = Field(default="", description="Title to be displayed")
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
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
                description="""Extra keyword arguments that are passed to `dcc.Dropdown` and overwrite any
defaults chosen by the Vizro team. This may have unexpected behavior.
Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/dropdown)
to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
underlying component may change in the future.""",
            ),
        ]
    ]

    # Consider making the _dynamic public later. The same property could also be used for all other components.
    # For example: vm.Graph could have a dynamic that is by default set on True.
    _dynamic: bool = PrivateAttr(False)
    _in_container: bool = PrivateAttr(False)
    _inner_component_properties: list[str] = PrivateAttr(dcc.Dropdown().available_properties)

    # Reused validators
    _validate_options = model_validator(mode="before")(validate_options_dict)

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

    def __call__(self, options):
        dict_options, default_value = get_dict_options_and_default(options=options, multi=self.multi)

        value = self.value if self.value is not None else default_value
        if self.multi and not isinstance(value, list):
            value = cast(MultiValueType, [value])

        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "options": dict_options,
            "value": value,
            "multi": self.multi,
            "persistence": True,
            "persistence_type": "session",
            "placeholder": "Select option",
            "className": "dropdown",
            "clearable": self.multi,  # Set clearable=False only for single-select dropdowns
        }

        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description], html_for=self.id
                )
                if self.title
                else None,
                dcc.Dropdown(**(defaults | self.extra)),
            ]
        )

    def _build_dynamic_placeholder(self):
        # Setting self.value is kind of Dropdown pre_build method. It sets self.value only the first time if it's None.
        # We cannot create pre_build for the Dropdown because it has to be called after vm.Filter.pre_build, but nothing
        # guarantees that. We can call Filter.selector.pre_build() from the Filter.pre_build() method if we decide that.
        # TODO: move this to pre_build once we have better control of the ordering.
        if self.value is None:
            _, default_value = get_dict_options_and_default(options=self.options, multi=self.multi)
            self.value = default_value

        # The rest of the method is added instead of calling and returning the content from the __call__ method
        # because placeholder for the Dropdown can't be the dropdown itself. The reason is that the Dropdown value can
        # be unexpectedly changed when the new options are added. This is developed as the dash feature
        # https://github.com/plotly/dash/pull/1970.
        plh_model, plh_options = (dcc.Checklist, self.value) if self.multi else (dbc.RadioItems, [self.value])

        description = self.description.build().children if self.description else [None]
        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description], html_for=self.id
                ),
                plh_model(
                    id=self.id,
                    options=plh_options,
                    value=self.value,
                    persistence=True,
                    persistence_type="session",
                ),
            ]
        )

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
