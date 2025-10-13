import math
from datetime import date
from typing import Annotated, Any, Literal, Optional, Union, cast

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import AfterValidator, BeforeValidator, Field, PrivateAttr, StrictBool, ValidationInfo, model_validator
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


def _get_list_of_labels(full_options: OptionsType) -> Union[list[StrictBool], list[float], list[str], list[date]]:
    """Returns a list of labels from the selector options provided."""
    if all(isinstance(option, dict) for option in full_options):
        return [option["label"] for option in full_options]  # type: ignore[index]
    else:
        return cast(Union[list[StrictBool], list[float], list[str], list[date]], full_options)


def _calculate_option_height(full_options: OptionsType, char_count: int) -> int:
    """Calculates the height of the dropdown options based on the longest option."""
    # We look at the longest option to find number_of_lines it requires. Option height is the same for all options
    # and needs 24px for each line + 8px padding.
    list_of_labels = _get_list_of_labels(full_options)
    max_length = max(len(str(option)) for option in list_of_labels)
    number_of_lines = math.ceil(max_length / char_count)
    return 8 + 24 * number_of_lines


class Dropdown(VizroBaseModel):
    """Categorical single/multi-option selector `Dropdown`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter].

    Abstract: Usage documentation
        [How to use categorical selectors](../user-guides/selectors.md#categorical-selectors)

    Args:
        type (Literal["dropdown"]): Defaults to `"dropdown"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[Union[SingleValueType, MultiValueType]]): See
            [`SingleValueType`][vizro.models.types.SingleValueType] and
            [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        multi (bool): Whether to allow selection of multiple values. Defaults to `True`.
        title (str): Title to be displayed. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dcc.Dropdown` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/dropdown)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["dropdown"] = "dropdown"
    options: OptionsType = []
    value: Annotated[
        Optional[Union[SingleValueType, MultiValueType]],
        AfterValidator(validate_value),
        Field(default=None, validate_default=True),
    ]
    multi: Annotated[
        bool,
        AfterValidator(validate_multi),
        Field(default=True, description="Whether to allow selection of multiple values", validate_default=True),
    ]
    title: str = Field(default="", description="Title to be displayed")
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
            underlying component may change in the future. Defaults to `{}`.""",
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
        # 24 characters is roughly the number of "A" characters you can fit comfortably on a line in the page dropdown
        # (placed on the left-side 280px width). 15 is the width for when the dropdown is in a container's controls.
        # "A" is representative of a slightly wider than average character:
        # https://stackoverflow.com/questions/3949422/which-letter-of-the-english-alphabet-takes-up-most-pixels
        option_height = _calculate_option_height(dict_options, 15 if self._in_container else 24)

        value = self.value if self.value is not None else default_value

        if self.multi:
            self._update_dropdown_select_all()
            value = value if isinstance(value, list) else [value]  # type: ignore[assignment]
            dict_options = [
                {
                    "label": dbc.Checkbox(
                        id=f"{self.id}_select_all",
                        value=len(value) == len(dict_options),  # type: ignore[arg-type]
                        label="Select All",
                        persistence=True,
                        persistence_type="session",
                        className="dropdown-select-all",
                    ),
                    # Special sentinel value used in update_dropdown_select_all.
                    # This never gets sent to the server.
                    "value": "__SELECT_ALL",
                },
                *dict_options,
            ]

        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "options": dict_options,
            "value": value,
            "multi": self.multi,
            "optionHeight": option_height,
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
        if self.multi:
            # Add the clientside callback as the callback has to be defined in the page.build process.
            self._update_dropdown_select_all()
            # hidden_select_all_dropdown is needed to ensure that clientside callback doesn't raise the no output error.
            hidden_select_all_dropdown = [dcc.Dropdown(id=f"{self.id}_select_all", style={"display": "none"})]
            placeholder_model = dcc.Checklist
            placeholder_options = self.value
        else:
            hidden_select_all_dropdown = [None]
            placeholder_model = dbc.RadioItems
            placeholder_options = [self.value]  # type: ignore[assignment]

        description = self.description.build().children if self.description else [None]
        return html.Div(
            children=[
                dbc.Label(
                    children=[html.Span(id=f"{self.id}_title", children=self.title), *description], html_for=self.id
                ),
                placeholder_model(
                    id=self.id,
                    options=placeholder_options,
                    value=self.value,
                    persistence=True,
                    persistence_type="session",
                ),
                *hidden_select_all_dropdown,
            ]
        )

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)

    def _update_dropdown_select_all(self):
        """Define the clientside callbacks in the page build phase responsible for handling the select_all."""
        clientside_callback(
            ClientsideFunction(namespace="dropdown", function_name="update_dropdown_select_all"),
            output=[
                Output(f"{self.id}_select_all", "value"),
                Output(self.id, "value", allow_duplicate=True),
            ],
            inputs=[
                Input(self.id, "value"),
                State(self.id, "options"),
            ],
            prevent_initial_call="initial_duplicate",
        )
