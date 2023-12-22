from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional

from dash import html

try:
    from pydantic.v1 import validator, Field
except ImportError:  # pragma: no cov
    from pydantic import validator, Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, get_unique_grid_component_ids
from vizro.models.types import ComponentType

if TYPE_CHECKING:
    from vizro.models import Layout


class Container(VizroBaseModel):
    type: Literal["container"] = "container"
    components: List[ComponentType]
    title: str = Field(..., description="Title to be displayed.")
    layout: Layout = None  # type: ignore[assignment]

    @validator("components", always=True)
    def set_components(cls, components):
        if not components:
            raise ValueError("Ensure this value has at least 1 item.")
        return components

    @validator("layout", always=True)
    def set_layout(cls, layout, values) -> Layout:
        from vizro.models import Layout
        if "components" not in values:
            return layout

        if layout is None:
            grid = [[i] for i in range(len(values["components"]))]
            return Layout(grid=grid)

        unique_grid_idx = get_unique_grid_component_ids(layout.grid)
        if len(unique_grid_idx) != len(values["components"]):
            raise ValueError("Number of page and grid components need to be the same.")
        return layout

    @_log_call
    def build(self):
        components_content = [
            html.Div(
                component.build(),
                style={
                    "gridColumn": f"{grid_coord.col_start}/{grid_coord.col_end}",
                    "gridRow": f"{grid_coord.row_start}/{grid_coord.row_end}",
                },
            )
            for component, grid_coord in zip(self.components, self.layout.component_grid_lines)
        ]
        components_container = self._create_component_container(components_content)

        # TODO: Perhaps there is a better name for: className="container-container"
        return html.Div(children=[html.H3(self.title), components_container], className="container")

    def _create_component_container(self, components_content):
        component_container = html.Div(
            children=[
                html.Div(
                    components_content,
                    style={
                        "gridRowGap": self.layout.row_gap,
                        "gridColumnGap": self.layout.col_gap,
                        "gridTemplateColumns": f"repeat({len(self.layout.grid[0])},"
                                               f"minmax({self.layout.col_min_width}, 1fr))",
                        "gridTemplateRows": f"repeat({len(self.layout.grid)},"
                                            f"minmax({self.layout.row_min_height}, 1fr))",
                    },
                    className="component_container_grid",
                ),
            ],
            className="components-container",
        )
        return component_container
