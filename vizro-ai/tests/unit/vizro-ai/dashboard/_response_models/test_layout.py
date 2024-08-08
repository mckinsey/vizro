import pytest
import vizro.models as vm
from tests_utils.asserts import assert_component_equal
from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.layout import LayoutPlan, _convert_to_grid


class TestLayoutPlan:
    """Test layout creation."""

    def test_structured_output_layout_create(self, fake_llm_layout, layout_description, layout):
        structured_output = _get_pydantic_model(
            query=layout_description, llm_model=fake_llm_layout, response_model=vm.Layout, df_info=None
        )
        assert_component_equal(structured_output.build(), layout, keys_to_strip={"id"})

    def test_layout_plan(self, layout):
        layout_plan = LayoutPlan(
            layout_grid_template_areas=["graph card"],
        )
        actual_layout = layout_plan.create(["graph", "card"])

        assert_component_equal(actual_layout.build(), layout, keys_to_strip={"id"})


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
            [],
        ),
        (
            ["card_1 scatter_plot scatter_plot", ". scatter_plot scatter_plot"],
            ["card_1", "scatter_plot"],
            [[0, 1, 1], [-1, 1, 1]],
        ),
    ],
)
def test_convert_to_grid(layout_grid_template_areas, component_ids, grid):
    actual_grid = _convert_to_grid(layout_grid_template_areas=layout_grid_template_areas, component_ids=component_ids)

    assert actual_grid == grid
