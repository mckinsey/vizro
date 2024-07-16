import pytest
from vizro_ai.dashboard.nodes.plan import DashboardPlanner, PagePlanner, create_filter_proxy

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


class TestComponentCreate:
    """Tests component creation."""

    @pytest.mark.xfail(raises=ValueError, reason="Known issue: real model is required for .plot")
    def test_card_create(self, component_card, fake_llm):
        if component_card.component_type == "Card":
            actual = component_card.create(
                model=fake_llm,
                df_metadata=None,
            )
        assert actual.type == "card"


class TestDashboardPlanner:
    """Tests dashboard planner."""

    @pytest.fixture
    def page_plan(self, component_card):
        return PagePlanner(
            title="Test Page",
            components=[component_card],
            controls=[],
            layout=None,
        )

    def test_dashboard_planner(self, page_plan):
        dashboard_plan = DashboardPlanner(
            title="Test Dashboard",
            pages=[page_plan],
        )
        assert dashboard_plan.pages[0].title == "Test Page"
        assert dashboard_plan.pages[0].components[0].component_id == "card_1"
        assert dashboard_plan.pages[0].components[0].component_type == "Card"
        assert dashboard_plan.pages[0].components[0].component_description == "This is a card"
        assert dashboard_plan.pages[0].components[0].page_id == "page_1"
        assert dashboard_plan.pages[0].components[0].df_name == "N/A"


class TestControlCreate:
    """Tests control creation."""

    def test_create_filter_proxy(self, df_cols, available_components):
        actual = create_filter_proxy(df_cols, available_components)
        with pytest.raises(ValidationError):
            actual(targets="gdp_chart", column="x")
