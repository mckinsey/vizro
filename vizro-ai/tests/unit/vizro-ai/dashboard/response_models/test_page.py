import pytest
from vizro_ai.dashboard.response_models.page import PagePlanner

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


class TestPagePlanner:
    """Test for page planner."""

    def test_dashboard_planner(self, component_card):
        page_plan = PagePlanner(
            title="Test Page",
            components_plan=[component_card],
            controls_plan=[],
            layout_plan=None,
            page_id="page_1",
        )
        assert page_plan.title == "Test Page"
        assert page_plan.components_plan[0].component_id == "card_1"
        assert page_plan.components_plan[0].component_type == "Card"
        assert page_plan.components_plan[0].component_description == "This is a card"
        assert page_plan.layout_plan is None
        assert page_plan.controls_plan == []

    def test_page_planner_invalid_components(self):
        with pytest.raises(ValidationError, match="A page must contain at least one component."):
            PagePlanner(
                title="Test Page",
                components_plan=[],
                controls_plan=[],
                layout_plan=None,
                page_id="page_1",
            )

    def test_page_planner_duplicate_components(self, component_card):
        with pytest.raises(ValidationError):
            PagePlanner(
                title="Test Page",
                components_plan=[component_card, component_card],
                controls_plan=[],
                layout_plan=None,
                page_id="page_2",
            )
