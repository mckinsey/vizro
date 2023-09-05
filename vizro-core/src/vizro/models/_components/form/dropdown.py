from typing import List, Literal, Optional, Union

from dash import dcc, html
from pydantic import Field, root_validator, validator

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default
from vizro.models._models_utils import _build_component_actions, _log_call
from vizro.models.types import MultiValueType, OptionsType, SingleValueType


def is_value_contained(value: Union[SingleValueType, MultiValueType], options: OptionsType):
    """Checks if value is contained in a list."""
    if isinstance(value, list):
        return all(item in options for item in value)
    else:
        return value in options


class Dropdown(VizroBaseModel):
    """Categorical multi-selector `Dropdown` to be provided to [`Filter`][vizro.models.Filter].

    Args:
        type (Literal["dropdown"]): Defaults to `"dropdown"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[Union[SingleValueType, MultiValueType]]): See
            [`SingleValueType`][vizro.models.types.SingleValueType] and
            [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        multi (bool): Whether to allow selection of multiple values. Defaults to `True`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["dropdown"] = "dropdown"
    options: OptionsType = []  # type: ignore[assignment]
    value: Optional[Union[SingleValueType, MultiValueType]] = None
    multi: bool = Field(True, description="Whether to allow selection of multiple values")
    title: Optional[str] = Field(None, description="Title to be displayed")
    actions: List[Action] = []

    # validator
    set_actions = _action_validator_factory("value")  # type: ignore[pydantic-field]

    @root_validator(pre=True)
    def validate_options_dict(cls, values):
        if "options" not in values or not isinstance(values["options"], list):
            return values

        for entry in values["options"]:
            if isinstance(entry, dict) and not set(entry.keys()) == {"label", "value"}:
                raise ValueError(
                    "Invalid argument `options` passed into Dropdown. Expected a dict with keys `label` and `value`."
                )
        return values

    @validator("value", always=True)
    def validate_value(cls, value, values):
        if "options" not in values or not values["options"]:
            return value

        possible_values = (
            [entry["value"] for entry in values["options"]]
            if isinstance(values["options"][0], dict)
            else values["options"]
        )

        if value and not is_value_contained(value, possible_values):
            raise ValueError("Please provide a valid value from `options`.")

        return value

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

        return html.Div(
            [
                *_build_component_actions(self),
                html.P(self.title, id="dropdown_title") if self.title else None,
                dcc.Dropdown(
                    id=self.id,
                    options=full_options,
                    value=self.value if self.value is not None else default_value,
                    multi=self.multi,
                    persistence=True,
                    clearable=False,
                ),
            ],
            className="selector_dropdown_container",
        )
