from typing import Literal, Union

import vizro.models as vm

# Entirely new component (actually exists, but for ease of explanation chosen)
SingleOptionType = Union[bool, float, str]
MultiOptionType = Union[list[bool], list[float], list[str]]


class CustomDropdown(vm.Dropdown):
    """Custom Dropdown that has multi=False as default."""

    type: Literal["custom-dropdown"] = "custom-dropdown"

    def build(self):
        dropdown_obj = super().build()
        dropdown_obj[self.id].multi = False
        return dropdown_obj


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", CustomDropdown)
