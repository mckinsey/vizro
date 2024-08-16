import pytest
import vizro.models as vm
from vizro_ai.dashboard._response_models.components import ComponentPlan


class TestComponentCreate:
    """Tests component creation."""

    def test_component_plan_instantiation(self):
        component = ComponentPlan(
            component_id="card_1",
            component_type="Card",
            component_description="This is a card",
            df_name="N/A",
        )
        assert component.component_id == "card_1"
        assert component.component_type == "Card"
        assert component.component_description == "This is a card"
        assert component.df_name == "N/A"

    @pytest.mark.xfail(raises=ValueError, reason="Known issue: real model is required for .plot")
    def test_card_create(self, component_plan_card, fake_llm_card):
        if component_plan_card.component_type == "Card":
            actual = component_plan_card.create(
                model=fake_llm_card,
                all_df_metadata=None,
            )
        assert actual.type == "card"

    def test_graph_create_valid(self, mocker, component_plan_graph, mock_vizro_ai_return, df_metadata):
        mock_vizro_ai_object = mocker.patch("vizro_ai.VizroAI.__init__")
        mock_vizro_ai_object.return_value = None
        mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI.plot")
        mock_vizro_ai_call.return_value = mock_vizro_ai_return
        result = component_plan_graph.create(
            model=None,
            all_df_metadata=df_metadata,
        )
        expected = vm.Graph(id="mock_id", figure=mock_vizro_ai_return)

        assert result.dict(exclude={"id": True}) == expected.dict(
            exclude={"id": True}
        )

    def test_card_create_valid(self, mocker, fake_llm_card, component_plan_card, expected_card):
        mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI")
        # Define the mock return value
        mock_vizro_ai_call.return_value = vm.Card(text="This is card.")

        result = component_plan_card.create(
            model=fake_llm_card,
            all_df_metadata=None,
        )

        assert result.dict(exclude={"id": True}) == expected_card.dict(
            exclude={"id": True}
        )

    def test_ag_grid_create_valid(
        self,
        component_plan_ag_grid,
        mock_vizro_ai_return_ag_grid,
        df_metadata,
    ):
        result = component_plan_ag_grid.create(
            model=None,
            all_df_metadata=df_metadata,
        )
        expected = vm.AgGrid(id="mock", figure=mock_vizro_ai_return_ag_grid)

        assert result.dict(exclude={"id": True, "figure": True}) == expected.dict(exclude={"id": True, "figure": True})
