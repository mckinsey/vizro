from typing import Annotated, Literal, Optional, Union

from dash import dcc, html
from pydantic import AfterValidator, Field, PlainSerializer, PrivateAttr

import vizro.models as vm
from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._base import VizroBaseModel, _log_call

# Case 2: Entirely new component (actually exists, but for ease of explanation chosen)
SingleOptionType = Union[bool, float, str]
MultiOptionType = Union[list[bool], list[float], list[str]]


class NewDropdown(VizroBaseModel):
    """Categorical single/multi-selector `Dropdown` to be provided to `Filter`."""

    type: Literal["new-dropdown"] = "new-dropdown"
    options: Optional[MultiOptionType] = Field(default=None, description="Possible options the user can select from")
    value: Optional[Union[SingleOptionType, MultiOptionType]] = Field(
        default=None, description="Options that are selected by default"
    )
    multi: bool = Field(default=True, description="Whether to allow selection of multiple values")
    actions: Annotated[
        list[Action],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]
    title: Optional[str] = Field(None, description="Title to be displayed")

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    @_log_call
    def build(self):
        full_options = self.options

        return html.Div(
            [
                html.P(self.title) if self.title else None,
                dcc.Dropdown(
                    id=self.id,
                    options=full_options,
                    value=self.value or full_options[0],
                    multi=self.multi,
                    persistence=True,
                    clearable=False,
                ),
            ],
        )


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", NewDropdown)
vm.Parameter.add_type("selector", NewDropdown)
