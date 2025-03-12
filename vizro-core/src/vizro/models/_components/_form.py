from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Optional, cast

from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist

from vizro.models import VizroBaseModel
from vizro.models._components.form import Checklist, Dropdown, RadioItems, RangeSlider, Slider
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, check_captured_callable_model
from vizro.models.types import _FormComponentType

if TYPE_CHECKING:
    from vizro.models import Layout


class Form(VizroBaseModel):
    """Container for all form components to be provided to [`Page`][vizro.models.Page].

    Args:
        type (Literal["form"]): Defaults to `"form"`.
        components (list[FormComponentType]): List of components used in the form.
        layout (Optional[Layout]): Defaults to `None`.

    """

    type: Literal["form"] = "form"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(Annotated[_FormComponentType, BeforeValidator(check_captured_callable_model)], min_length=1)  # type: ignore[valid-type]
    layout: Annotated[Optional[Layout], AfterValidator(set_layout), Field(default=None, validate_default=True)]

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
        self.layout = cast(
            Layout,  # cannot actually be None if you check components and layout field together
            self.layout,
        )
        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()
        return html.Div(id=self.id, children=components_container)
