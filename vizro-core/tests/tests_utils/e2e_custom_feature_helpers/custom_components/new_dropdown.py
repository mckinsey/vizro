from typing import List, Optional, Union

from dash import dcc, html

import vizro.models as vm

try:
    from pydantic.v1 import Field, PrivateAttr
except ImportError:
    from pydantic import Field, PrivateAttr
from typing_extensions import Literal

from vizro.models import Action
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._base import VizroBaseModel, _log_call

# Case 2: Entirely new component (actually exists, but for ease of explanation chosen)
SingleOptionType = Union[bool, float, str]
MultiOptionType = Union[List[bool], List[float], List[str]]


class NewDropdown(VizroBaseModel):
    """Categorical single/multi-selector `Dropdown` to be provided to `Filter`."""

    type: Literal["new-dropdown"] = "new-dropdown"
    options: Optional[MultiOptionType] = Field(None, description="Possible options the user can select from")
    value: Optional[Union[SingleOptionType, MultiOptionType]] = Field(
        None, description="Options that are selected by default"
    )
    multi: bool = Field(True, description="Whether to allow selection of multiple values")
    actions: List[Action] = []
    title: Optional[str] = Field(None, description="Title to be displayed")

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        full_options = self.options if self.multi else self.options

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
