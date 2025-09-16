import logging

import pytest
import vizro.models as vm

from vizro_ai.dashboard._response_models.layout import LayoutPlan


class TestLayoutCreate:
    """Test layout creation."""

    @pytest.mark.parametrize(
        "layout_grid_template_areas, component_ids, grid",
        [
            (
                ["card_1 scatter_plot scatter_plot", "card_2 scatter_plot scatter_plot"],
                ["card_1", "scatter_plot", "card_2"],
                [[0, 1, 1], [2, 1, 1]],
            ),
            (
                ["card_1 scatter_plot scatter_plot", ". scatter_plot scatter_plot"],
                ["card_1", "scatter_plot"],
                [[0, 1, 1], [-1, 1, 1]],
            ),
        ],
    )
    def test_layout_create_valid(self, layout_grid_template_areas, component_ids, grid):
        layout_plan = LayoutPlan(
            layout_grid_template_areas=layout_grid_template_areas,
        )
        result = layout_plan.create(component_ids=component_ids)
        expected = vm.Layout(grid=grid)

        assert result.model_dump(exclude={"id": True}) == expected.model_dump(exclude={"id": True})

    @pytest.mark.parametrize(
        "layout_grid_template_areas, component_ids, error_message",
        [
            (
                ["card_1 scatter_plot scatter_plot", "card_2 scatter_plot scatter_plot"],
                ["card_1", "scatter_plot"],
                "Build failed for `Layout",
            ),
            (
                ["card_1 scatter_plot scatter_plot", "card_2 card_2 scatter_plot"],
                ["card_1", "scatter_plot", "card_2"],
                "Calculated grid which caused the error:",
            ),
        ],
    )
    def test_layout_create_invalid(self, layout_grid_template_areas, component_ids, error_message, caplog):
        layout_plan = LayoutPlan(
            layout_grid_template_areas=layout_grid_template_areas,
        )

        with caplog.at_level(logging.WARNING):
            result = layout_plan.create(component_ids=component_ids)

        assert error_message in caplog.text
        assert result is None
