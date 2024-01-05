from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from dash import html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import (
    _assign_component_grid_area,
    _create_component_container,
    _log_call,
    set_components,
    set_layout,
)
from vizro.models.types import ComponentType

if TYPE_CHECKING:
    from vizro.models import Layout


class Container(VizroBaseModel):
    """A page in [`Dashboard`][vizro.models.Dashboard] with its own URL path and place in the `Navigation`.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (List[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        layout (Layout): Layout to place components in. Defaults to `None`.

    Raises:
        ValueError: If number of page and grid components is not the same
    """

    type: Literal["container"] = "container"
    components: List[ComponentType]
    title: str = Field(..., description="Title to be displayed.")
    layout: Layout = None  # type: ignore[assignment]

    # Re-used validators
    _validate_components = validator("components", allow_reuse=True, always=True)(set_components)
    _validate_layout = validator("layout", allow_reuse=True, always=True)(set_layout)

    @_log_call
    def build(self):
        components_content = _assign_component_grid_area(self)
        components_container = _create_component_container(self, components_content)
        return html.Div(children=[html.H3(self.title), components_container], className="page-component-container")
