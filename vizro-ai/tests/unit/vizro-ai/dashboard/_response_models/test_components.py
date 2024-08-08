import pytest
import vizro.models as vm
from tests_utils.asserts import assert_component_equal
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


def test_card_create_valid(mocker, fake_llm_card, component_card, df):
    mock_vizro_ai_call = mocker.patch("vizro_ai.VizroAI")
    # Define the mock return value
    mock_vizro_ai_call.return_value = vm.Card(text="This is card.")

    result = component_card.create(
        model=fake_llm_card,
        all_df_metadata=None,
    )

    assert_component_equal(result.build(), vm.Card(text="this is a card").build(), keys_to_strip={"id"})
