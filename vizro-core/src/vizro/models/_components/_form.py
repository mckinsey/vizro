from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from dash import html

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._components.form import Checklist, Dropdown, RadioItems, RangeSlider, Slider
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, _validate_min_length
from vizro.models.types import _FormComponentType

if TYPE_CHECKING:
    from vizro.models import Layout


class Form(VizroBaseModel):
    """Container for all form components to be provided to [`Page`][vizro.models.Page].

    Args:
        type (Literal["form"]): Defaults to `"form"`.
        components (List[FormComponentType]): List of components used in the form.
        layout (Layout): Defaults to `None`.

    """

    type: Literal["form"] = "form"
    components: List[_FormComponentType]
    layout: Layout = None  # type: ignore[assignment]

    # Re-used validators
    _validate_components = validator("components", allow_reuse=True, always=True)(_validate_min_length)
    _validate_layout = validator("layout", allow_reuse=True, always=True)(set_layout)

    @_log_call
    def pre_build(self):
        for component in self.components:
            if isinstance(component, (Slider, RangeSlider)):
                if component.min is None or component.max is None:
                    raise TypeError(f"{component.type} requires the arguments 'min' and 'max' when used within Form.")

            if isinstance(component, (Checklist, Dropdown, RadioItems)) and not component.options:
                raise TypeError(f"{component.type} requires the argument 'options' when used within Form.")

    @_log_call
    def build(self):
        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()
        return html.Div(components_container, id=self.id)
