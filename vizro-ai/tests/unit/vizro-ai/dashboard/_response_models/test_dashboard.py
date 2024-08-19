from vizro_ai.dashboard._response_models.dashboard import DashboardPlan


class TestDashboardCreate:
    """Tests dashboard plan creation."""

    def test_dashboard_plan_instantiation(self, page_plan):
        dashboard_plan = DashboardPlan(
            title="Test Dashboard",
            pages=[page_plan],
        )
        assert dashboard_plan.pages[0].title == "Test Page"
        assert dashboard_plan.pages[0].components_plan[0].component_id == "card_1"
        assert dashboard_plan.pages[0].components_plan[0].component_type == "Card"
        assert dashboard_plan.pages[0].components_plan[0].component_description == "This is a card"
        assert dashboard_plan.pages[0].components_plan[0].df_name == "N/A"
        assert dashboard_plan.pages[0].layout_plan is None
        assert dashboard_plan.pages[0].controls_plan == []
