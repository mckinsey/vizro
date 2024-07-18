"""Layout plan model."""

import logging
from typing import List, Union

import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, validator
import numpy as np
from vizro.models._layout import _get_grid_lines, _get_unique_grid_component_ids, _validate_grid_areas
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


# TODO: try switch to inherit from Layout directly, like FilterProxy
class LayoutProxyModel(BaseModel):
    """Proxy model for Layout."""

    grid: List[List[int]] = Field(..., description="Grid specification to arrange components on screen.")

    @validator("grid")
    def validate_grid(cls, grid):
        """Validate the grid."""
        if len({len(row) for row in grid}) > 1:
            raise ValueError("All rows must be of same length.")

        # Validate grid type and values
        unique_grid_idx = _get_unique_grid_component_ids(grid)
        if 0 not in unique_grid_idx or not np.array_equal(unique_grid_idx, np.arange((unique_grid_idx.max() + 1))):
            raise ValueError("Grid must contain consecutive integers starting from 0.")

        # Validates grid areas spanned by components and spaces
        component_grid_lines, space_grid_lines = _get_grid_lines(grid)
        _validate_grid_areas(component_grid_lines + space_grid_lines)
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
        "Each unique string should be used to represent a unique component. If no grid template areas are provided, "
        "leave this as an empty list.",
    )

    def create(self, model) -> Union[vm.Layout, None]:
        """Create the layout."""
        layout_prompt = (
            f"Create a layout from the following instructions: {self.layout_description}. Do not make up "
            f"a layout if not requested. If a layout_grid_template_areas is provided, translate it into "
            f"a matrix of integers where each integer represents a unique component (starting from 0). replace "
            f"'.' with -1 to represent empty spaces. Here is the grid template areas: {self.layout_grid_template_areas}"
        )
        if self.layout_description == "N/A":
            return None

        try:
            proxy = _get_pydantic_output(query=layout_prompt, llm_model=model, result_model=LayoutProxyModel)
            actual = vm.Layout.parse_obj(proxy.dict(exclude={}))
        except DebugFailure as e:
            logger.warning(
                f"Build failed for `Layout`, returning default values. Try rephrase the prompt or "
                f"select a different model. \n ------- \n Error details: {e} \n ------- \n "
                f"Relevant prompt: `{self.layout_description}`"
            )
            actual = None

        return actual


if __name__ == "__main__":
    from vizro_ai.chains._llm_models import _get_llm_model

    model = _get_llm_model()
    layout_plan = LayoutPlan(
        layout_description="Create a layout with a graph on the left and a card on the right.",
        layout_grid_template_areas=["graph card"],
    )
    layout = layout_plan.create(model)
    print(layout)  # noqa: T201
    print(layout.dict())  # noqa: T201
