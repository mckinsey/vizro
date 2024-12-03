import math
from datetime import date
from typing import Literal, Optional, Union

from dash import dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, StrictBool, root_validator, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, StrictBool, root_validator, validator

import dash_bootstrap_components as dbc

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default, validate_options_dict, validate_value
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, OptionsType, SingleValueType


def _get_list_of_labels(full_options: OptionsType) -> Union[list[StrictBool], list[float], list[str], list[date]]:
    """Returns a list of labels from the selector options provided."""
    if all(isinstance(option, dict) for option in full_options):
        return [option["label"] for option in full_options]  # type: ignore[index]
    else:
        return full_options


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
    value: Optional[Union[SingleValueType, MultiValueType]] = None
    multi: bool = Field(True, description="Whether to allow selection of multiple values")
    title: str = Field("", description="Title to be displayed")
    actions: list[Action] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Re-used validators
    _set_actions = _action_validator_factory("value")
    _validate_options = root_validator(allow_reuse=True, pre=True)(validate_options_dict)
    _validate_value = validator("value", allow_reuse=True, always=True)(validate_value)

    @validator("multi", always=True)
    def validate_multi(cls, multi, values):
        if "value" not in values:
            return multi

        if values["value"] and multi is False and isinstance(values["value"], list):
            raise ValueError("Please set multi=True if providing a list of default values.")
        return multi

    @_log_call
    def build(self):
        full_options, default_value = get_options_and_default(options=self.options, multi=self.multi)
        option_height = _calculate_option_height(full_options)

        return html.Div(
            children=[
                dbc.Label(self.title, html_for=self.id) if self.title else None,
                dcc.Dropdown(
                    id=self.id,
                    options=full_options,
                    value=self.value if self.value is not None else default_value,
                    multi=self.multi,
                    persistence=True,
                    optionHeight=option_height,
                    persistence_type="session",
                ),
            ]
        )
