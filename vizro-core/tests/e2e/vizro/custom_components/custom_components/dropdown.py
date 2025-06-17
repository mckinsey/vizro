from typing import Literal

import vizro.models as vm


class CustomDropdown(vm.Dropdown):
    """Custom Dropdown that has multi=False as default."""

    type: Literal["custom-dropdown"] = "custom-dropdown"
    multi: bool = False

    def build(self):
        dropdown_obj = super().build()
        return dropdown_obj


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", CustomDropdown)
