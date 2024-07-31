import pytest
import vizro.models as vm
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.dashboard.response_models.layout import LayoutPlan, _convert_to_grid


class TestLayoutPlan:
    """Test layout creation."""

    def test_structured_output_layout_create(self, fake_llm_layout, layout_description):
        structured_output = _get_pydantic_output(
            query=layout_description, llm_model=fake_llm_layout, response_model=vm.Layout, df_info=None
        )
        assert structured_output.dict(exclude={"id": True}) == vm.Layout(grid=[[0, 1]]).dict(exclude={"id": True})

    def test_layout_plan(self):
        layout_plan = LayoutPlan(
            layout_description="Create a layout with a graph on the left and a card on the right.",
            layout_grid_template_areas=["graph card"],
        )
        layout = layout_plan.create(["graph", "card"])

        assert layout.dict(exclude={"id": True}) == vm.Layout(grid=[[0, 1]]).dict(exclude={"id": True})

    def test_layout_plan_no_description(self, fake_llm_layout):
        layout_plan = LayoutPlan(
            layout_description="N/A",
            layout_grid_template_areas=["graph card"],
        )
        layout = layout_plan.create(fake_llm_layout)

        assert layout is None


@pytest.mark.parametrize(
    "layout_grid_template_areas, component_ids, grid",
    [
        (
            ["card_1 scatter_plot scatter_plot", "card_2 scatter_plot scatter_plot"],
            ["card_1", "scatter_plot", "card_2"],
            [[0, 1, 1], [2, 1, 1]],
        ),
        (
            ["card_1 scatter_plot scatter_plot", "card_2 scatter_plot scatter_plot"],
            ["card_1", "scatter_plot"],
            [[0, 1, 1], [-1, 1, 1]],
        ),
    ],
)
def test_convert_to_grid_valid(layout_grid_template_areas, component_ids, grid):
    actual_grid = _convert_to_grid(layout_grid_template_areas=layout_grid_template_areas, component_ids=component_ids)

    assert actual_grid == grid
