import pytest
from pydantic import ValidationError

from vizro_ai.dashboard._response_models.page import PagePlan


class TestPageCreate:
    """Test for page plan."""

    def test_page_plan_instantiation(self, component_plan_card):
        page_plan = PagePlan(
            title="Test Page",
            components_plan=[component_plan_card],
            controls_plan=[],
            layout_plan=None,
        )
        assert page_plan.title == "Test Page"
        assert page_plan.components_plan[0].component_id == "card_1"
        assert page_plan.components_plan[0].component_type == "Card"
        assert page_plan.components_plan[0].component_description == "This is a card"
        assert page_plan.layout_plan is None
        assert page_plan.controls_plan == []
        assert page_plan.unsupported_specs == []

    def test_page_plan_invalid_components(self):
        with pytest.raises(ValidationError, match="A page must contain at least one component."):
            PagePlan(
                title="Test Page",
                components_plan=[],
                controls_plan=[],
                layout_plan=None,
            )

    def test_page_plan_unsupported_specs(self, component_plan_card):
        page_plan = PagePlan(
            title="Test Page",
            components_plan=[component_plan_card],
            controls_plan=[],
            layout_plan=None,
            unsupported_specs=["Unknown"],
        )

        assert page_plan.unsupported_specs == []

    def test_page_plan_duplicate_components(self, component_plan_card):
        with pytest.raises(ValidationError):
            PagePlan(
                title="Test Page",
                components_plan=[component_plan_card, component_plan_card],
                controls_plan=[],
                layout_plan=None,
            )
