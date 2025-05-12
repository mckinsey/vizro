from typing import Annotated, Literal, Optional, Union

from dash import dcc, html
from pydantic import AfterValidator, Field, PlainSerializer

import vizro.models as vm
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._base import VizroBaseModel, _log_call
from vizro.models.types import ActionType

# Entirely new component (actually exists, but for ease of explanation chosen)
SingleOptionType = Union[bool, float, str]
MultiOptionType = Union[list[bool], list[float], list[str]]


class CustomDropdown(vm.Dropdown):
    """Custom Dropdown that has multi=False as default."""

    type: Literal["custom-dropdown"] = "custom-dropdown"

    def build(self):
        dropdown_obj = super().build()
        dropdown_obj[self.id].multi=False
        return dropdown_obj


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", CustomDropdown)
