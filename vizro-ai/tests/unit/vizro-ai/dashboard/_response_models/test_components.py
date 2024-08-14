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
    def test_card_create(self, component_card, fake_llm_card):
        if component_card.component_type == "Card":
            actual = component_card.create(
                model=fake_llm_card,
                all_df_metadata=None,
            )
        assert actual.type == "card"
        
    def test_graph_create_valid(self, mocker,component_plan_graph, mock_vizro_ai_return,fake_llm,df_metadata, df):
        mock_vizro_ai_object = mocker.patch("vizro_ai.VizroAI.__init__")
        mock_vizro_ai_object.return_value = None
        mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI.plot")
        mock_vizro_ai_call.return_value = mock_vizro_ai_return
        result = component_plan_graph.create(
            model=None,
            all_df_metadata=df_metadata,
        )
        expected = vm.Graph(
            id = "mock_id",
            figure = mock_vizro_ai_return
        )
        assert result.dict(exclude={"id": True}) == expected.dict(exclude={"id": True}) #TODO: this should really be assert_components_equal



def test_card_create_valid(mocker, fake_llm_card, component_card, df):
    mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI")
    # Define the mock return value
    mock_vizro_ai_call.return_value = vm.Card(text="This is card.")

    result = component_card.create(
        model=fake_llm_card,
        all_df_metadata=None,
    )

    assert result.dict(exclude={"id": True}) == vm.Card(text="this is a card").dict(exclude={"id": True})
