import math
from datetime import date
from typing import Annotated, Literal, Optional, Union, cast

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import AfterValidator, Field, PrivateAttr, StrictBool, ValidationInfo, model_validator
from pydantic.functional_serializers import PlainSerializer

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default, validate_options_dict, validate_value
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, OptionsDictType, OptionsType, SingleValueType


def _get_list_of_labels(full_options: OptionsType) -> Union[list[StrictBool], list[float], list[str], list[date]]:
    """Returns a list of labels from the selector options provided."""
    if all(isinstance(option, dict) for option in full_options):
        return [option["label"] for option in full_options]  # type: ignore[index]
    else:
        return cast(Union[list[StrictBool], list[float], list[str], list[date]], full_options)


def _calculate_option_height(full_options: OptionsType) -> int:
    """Calculates the height of the dropdown options based on the longest option."""
    # 30 characters is roughly the number of "A" characters you can fit comfortably on a line in the dropdown.
    # "A" is representative of a slightly wider than average character:
    # https://stackoverflow.com/questions/3949422/which-letter-of-the-english-alphabet-takes-up-most-pixels
    # We look at the longest option to find number_of_lines it requires. Option height is the same for all options
    # and needs 24px for each line + 8px padding.
    list_of_labels = _get_list_of_labels(full_options)
    max_length = max(len(str(option)) for option in list_of_labels)
    number_of_lines = math.ceil(max_length / 30)
    return 8 + 24 * number_of_lines


def validate_multi(multi, info: ValidationInfo):
    if "value" not in info.data:
        return multi

    if info.data["value"] and multi is False and isinstance(info.data["value"], list):
        raise ValueError("Please set multi=True if providing a list of default values.")
    return multi


def _add_select_all_option(full_options: OptionsType) -> OptionsType:
    """Adds a 'Select All' option to the list of options."""
    # TODO: Move option to dictionary conversion within `get_options_and_default` function as here: https://github.com/mckinsey/vizro/pull/961#discussion_r1923356781
    options_dict = [
        cast(OptionsDictType, {"label": option, "value": option}) if not isinstance(option, dict) else option
        for option in full_options
    ]

    options_dict[0] = {"label": html.Div(["ALL"]), "value": "ALL"}
    return options_dict


class Dropdown(VizroBaseModel):
    """Categorical single/multi-option selector `Dropdown`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown).

    Args:
        type (Literal["dropdown"]): Defaults to `"dropdown"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[Union[SingleValueType, MultiValueType]]): See
            [`SingleValueType`][vizro.models.types.SingleValueType] and
            [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        multi (bool): Whether to allow selection of multiple values. Defaults to `True`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

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
    actions: Annotated[
        list[Action],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    # Consider making the _dynamic public later. The same property could also be used for all other components.
    # For example: vm.Graph could have a dynamic that is by default set on True.
    _dynamic: bool = PrivateAttr(False)

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Reused validators
    _validate_options = model_validator(mode="before")(validate_options_dict)

    def __call__(self, options):
        full_options, default_value = get_options_and_default(options=options, multi=self.multi)
        option_height = _calculate_option_height(full_options)
        altered_options = _add_select_all_option(full_options=full_options) if self.multi else full_options

        return html.Div(
            children=[
                dbc.Label(self.title, html_for=self.id) if self.title else None,
                dcc.Dropdown(
                    id=self.id,
                    options=altered_options,
                    value=self.value if self.value is not None else default_value,
                    multi=self.multi,
                    optionHeight=option_height,
                    persistence=True,
                    persistence_type="session",
                    className="dropdown",
                ),
            ]
        )

    def _build_dynamic_placeholder(self):
        # Setting self.value is kind of Dropdown pre_build method. It sets self.value only the first time if it's None.
        # We cannot create pre_build for the Dropdown because it has to be called after vm.Filter.pre_build, but nothing
        # guarantees that. We can call Filter.selector.pre_build() from the Filter.pre_build() method if we decide that.
        # TODO: move this to pre_build once we have better control of the ordering.
        if self.value is None:
            _, default_value = get_options_and_default(self.options, self.multi)
            self.value = default_value

        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
