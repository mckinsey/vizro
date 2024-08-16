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

    def test_create_graph(self, mocker, component_plan_graph, mock_vizro_ai_return, df_metadata):
        mock_vizro_ai_object = mocker.patch("vizro_ai.VizroAI.__init__")
        mock_vizro_ai_object.return_value = None
        mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI.plot")
        mock_vizro_ai_call.return_value = mock_vizro_ai_return
        result = component_plan_graph.create(
            model=None,
            all_df_metadata=df_metadata,
        )
        expected = vm.Graph(id="mock_id", figure=mock_vizro_ai_return)

        assert result.dict(exclude={"id": True}) == expected.dict(exclude={"id": True})

    def test_create_card(self, fake_llm_card, component_plan_card, expected_card):
        result = component_plan_card.create(
            model=fake_llm_card,
            all_df_metadata=None,
        )

        assert result.dict(exclude={"id": True}) == expected_card.dict(exclude={"id": True})

    def test_create_ag_grid(
        self,
        mocker,
        component_plan_ag_grid,
        mock_dash_ag_grid,
        mock_return_ag_grid,
        df_metadata,
    ):
        mocker.patch(
            "vizro_ai.dashboard._response_models.components.ComponentPlan.create", return_value=mock_return_ag_grid
        )
        result = component_plan_ag_grid.create(
            model=None,
            all_df_metadata=df_metadata,
        )
        expected = vm.AgGrid(id="ag_grid", figure=mock_dash_ag_grid)

        assert result.dict(exclude={"id": True}) == expected.dict(exclude={"id": True})
