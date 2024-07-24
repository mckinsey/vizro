"""Layout plan model."""

import logging
from typing import List

import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


def _convert_to_grid(layout_grid_template_areas, component_ids) -> List[List[int]]:
    component_map = {component: index for index, component in enumerate(component_ids)}
    grid = []

    for row in layout_grid_template_areas:
        grid_row = []
        for cell in row.split():
            if cell == ".":
                grid_row.append(-1)
            else:
                try:
                    grid_row.append(component_map[cell])
                except KeyError:
                    logger.warning(f"Component {cell} not found in component_ids: {component_ids}")
                    grid_row.append(-1)
        grid.append(grid_row)

    return grid


class LayoutPlan(BaseModel):
    """Layout plan model, which only applies to Vizro Components(Graph, AgGrid, Card)."""

    layout_description: str = Field(
        ...,
        description="Description of the layout of Vizro Components(Graph, AgGrid, Card). "
        "Include everything that seems to relate to this layout. If layout not specified, describe layout as `N/A`.",
    )
    layout_grid_template_areas: List[str] = Field(
        [],
        description="Generate grid template areas for the layout adhering to the grid-template-areas CSS property "
        "syntax. Each unique string ('component_id' and 'page_id' concatenated by '_') should be used to represent "
        "a unique component. If a grid area is empty, use a dot ('.') to represent it."
        "Ensure that each row of the grid layout is represented by a string, with each grid area separated by a space."
        "Return the grid template areas as a list of strings, where each string corresponds to a row in the grid."
        "If no grid template areas are provided, return an empty list.",
    )

    def create(self, component_ids: List[str]):
        """Create the layout."""
        if self.layout_description == "N/A":
            return None

        try:
            grid = _convert_to_grid(
                layout_grid_template_areas=self.layout_grid_template_areas, component_ids=component_ids
            )
            actual = vm.Layout(grid=grid)
        except ValidationError as e:
            logger.warning(
                f"Build failed for `Layout`, returning default values. Try rephrase the prompt or "
                f"select a different model. \n ------- \n Error details: {e} \n ------- \n "
                f"Relevant prompt: `{self.layout_description}`, which was parsed as layout_grid_template_areas:"
                f" {self.layout_grid_template_areas}"
            )
            if grid:
                logger.warning(f"Calculated grid which caused the error: {grid}")
            actual = None

        return actual


if __name__ == "__main__":
    from vizro_ai.chains._llm_models import _get_llm_model

    model = _get_llm_model()
    layout_plan = LayoutPlan(
        layout_description="Create a layout with a graph on the left and a card on the right.",
        layout_grid_template_areas=["graph1 card2 card2", "graph1 . card1"],
    )
    layout = layout_plan.create(model, component_ids=["graph1", "card1", "card2"])
    print(layout)  # noqa: T201
