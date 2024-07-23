"""Layout plan model."""

import logging
from typing import List, Union

import vizro.models as vm
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from pydantic.v1 import BaseModel, Field, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


def _convert_to_grid(layout_grid_template_areas, component_ids):
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
        "Include everything that seems to relate"
        " to this layout AS IS. If layout not specified, describe layout as `N/A`.",
    )
    layout_grid_template_areas: List[str] = Field(
        [],
        description="Grid template areas for the layout, which adhere to the grid-template-areas CSS property syntax."
        "Each unique string ('component_id' and 'page_id' concated by '_') should be used to "
        "represent a unique component. If no grid template areas are provided, leave this as an empty list.",
    )

    def create(self, model: BaseChatModel, component_ids: List[str]) -> Union[vm.Layout, None]:
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
