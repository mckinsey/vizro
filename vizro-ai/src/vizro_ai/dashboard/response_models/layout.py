"""Layout plan model."""

import logging
from typing import List, Union

import vizro.models as vm
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from pydantic.v1 import BaseModel, Field, create_model
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, create_model
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


def _convert_layout_to_grid(layout_grid_template_areas):
    # TODO: Programmatically convert layout_grid_template_areas to grid
    pass


def _create_layout_proxy(component_ids, layout_grid_template_areas) -> BaseModel:
    """Create a layout proxy model."""

    def validate_grid(v):
        """Validate the grid."""
        expected_grid = _convert_layout_to_grid(layout_grid_template_areas)
        if v != expected_grid:
            logger.warning(f"Calculated grid: {expected_grid}, got: {v}")
            return v

    return create_model(
        "LayoutProxyModel",
        grid=(
            List[List[int]],
            Field(None, description="Grid specification to arrange components on screen."),
        ),
        __validators__={
            # "validator1": validator("grid", pre=True, allow_reuse=True)(validate_grid),
        },
        __base__=vm.Layout,
    )


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
        layout_prompt = (
            f"Create a layout from the following instructions: {self.layout_description}. Do not make up "
            f"a layout if not requested. If a layout_grid_template_areas is provided, translate it into "
            f"a matrix of integers where each integer represents a unique component (starting from 0). "
            f"When translating, match the layout_grid_template_areas element string to the same name in "
            f"{component_ids} and use the index of {component_ids} to replace the element string. "
            f"replace '.' with -1 to represent empty spaces. Here is the grid template areas: \n ------- \n"
            f" {self.layout_grid_template_areas}\n ------- \n"
        )
        if self.layout_description == "N/A":
            return None

        try:
            result_proxy = _create_layout_proxy(
                component_ids=component_ids, layout_grid_template_areas=self.layout_grid_template_areas
            )
            proxy = _get_pydantic_output(query=layout_prompt, llm_model=model, response_model=result_proxy)
            actual = vm.Layout.parse_obj(proxy.dict(exclude={"id": True}))
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
        layout_grid_template_areas=["graph1 card2 card2", "graph1 . card1"],
    )
    layout = layout_plan.create(model, component_ids=["graph1", "card1", "card2"])
    print(layout)  # noqa: T201
