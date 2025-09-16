"""Layout plan model."""

import logging
from typing import Optional

import vizro.models as vm
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


def _convert_to_grid(layout_grid_template_areas: list[str], component_ids: list[str]) -> list[list[int]]:
    component_map = {component: index for index, component in enumerate(component_ids)}
    grid = []

    for row in layout_grid_template_areas:
        grid_row = []
        for raw_cell in row.split():
            cell = raw_cell.strip("'\"")
            if cell == ".":
                grid_row.append(-1)
            else:
                try:
                    grid_row.append(component_map[cell])
                except KeyError:
                    logger.warning(
                        f"""
[FALLBACK] Component {cell} not found in component_ids: {component_ids}.
Returning default values.
"""
                    )
                    return []
        grid.append(grid_row)

    return grid


class LayoutPlan(BaseModel):
    """Layout plan model, which only applies to Vizro Components(Graph, AgGrid, Card)."""

    layout_grid_template_areas: list[str] = Field(
        default=[],
        description="""
        Generate grid template areas for the layout adhering to the grid-template-areas CSS property syntax.
        If no layout requested, return an empty list.
        If requested, represent each component by 'component_id'.
        IMPORTANT: Ensure that the `component_id` matches the `component_id` in the ComponentPlan.
        If a grid area is empty, use a single dot ('.') to represent it.
        Ensure that each row of the grid layout is represented by a string, with each grid area separated by a space.
        Return the grid template areas as a list of strings, where each string corresponds to a row in the grid.
        No more than 600 characters in total.
        """,
    )

    def create(self, component_ids: list[str]) -> Optional[vm.Layout]:
        """Create the layout."""
        if not self.layout_grid_template_areas:
            return None

        try:
            grid = _convert_to_grid(
                layout_grid_template_areas=self.layout_grid_template_areas, component_ids=component_ids
            )
            actual = vm.Layout(grid=grid)
        except ValidationError as e:
            logger.warning(
                f"""
[FALLBACK] Build failed for `Layout`, returning default values. Try rephrase the prompt or select a different model.
Error details: {e}
Relevant layout_grid_template_areas:
{self.layout_grid_template_areas}
"""
            )
            if grid:
                logger.warning(f"Calculated grid which caused the error: {grid}")
            actual = None

        return actual


if __name__ == "__main__":
    from vizro_ai._llm_models import _get_llm_model

    model = _get_llm_model()
    layout_plan = LayoutPlan(
        layout_grid_template_areas=["graph1 card2 card2", "graph1 . card1"],
    )
    layout = layout_plan.create(component_ids=["graph1", "card1", "card2"])
    print(layout)  # noqa: T201
