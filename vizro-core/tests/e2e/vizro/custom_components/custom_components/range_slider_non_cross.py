from typing import Literal

import vizro.models as vm


# Custom component based on existing component
class RangeSliderNonCross(vm.RangeSlider):
    """Custom numeric multi-selector `RangeSliderNonCross` to be provided to `Filter`."""

    type: Literal["other_range_slider"] = "other_range_slider"

    def build(self):
        range_slider_build_obj = super().build()
        range_slider_build_obj[self.id].allowCross = False
        range_slider_build_obj[self.id].tooltip = {
            "always_visible": True,
            "placement": "bottom",
        }
        return range_slider_build_obj


# Important: Add new components to expected type - here the selector of the parent components
vm.Filter.add_type("selector", RangeSliderNonCross)
vm.Parameter.add_type("selector", RangeSliderNonCross)
