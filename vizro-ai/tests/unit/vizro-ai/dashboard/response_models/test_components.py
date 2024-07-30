import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    pass


class TestComponentCreate:
    """Tests component creation."""

    @pytest.mark.xfail(raises=ValueError, reason="Known issue: real model is required for .plot")
    def test_card_create(self, component_card, fake_llm):
        if component_card.component_type == "Card":
            actual = component_card.create(
                model=fake_llm,
                all_df_metadata=None,
            )
        assert actual.type == "card"
