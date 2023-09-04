"""Unit tests for vizro.models.Card."""
import dash_bootstrap_components as dbc
import pytest
from dash import dcc
from pydantic import ValidationError

import vizro.models as vm


class TestCardInstantiation:
    """Tests model instantiation."""

    def test_create_card_mandatory_only(self):
        card = vm.Card(text="Text to test card")

        assert hasattr(card, "id")
        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.href is None

    @pytest.mark.parametrize("id, href", [("id_1", "/page_1_reference"), ("id_2", "https://www.google.de/")])
    def test_create_card_mandatory_and_optional(self, id, href):
        card = vm.Card(text="Text to test card", id=id, href=href)

        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.id == id
        assert card.href == href

    def test_mandatory_text_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Card()

    def test_none_as_text(self):
        with pytest.raises(ValidationError, match="none is not an allowed value"):
            vm.Card(text=None)


class TestBuildMethod:
    """Tests build method."""

    @pytest.mark.parametrize(
        "test_text, expected",
        [
            ("""# Header""", "# Header"),
            ("""_This **tests** emphasis_""", "_This **tests** emphasis_"),
            ("""> This tests blockquotes""", "> This tests blockquotes"),
            ("""* This tests list items""", "* This tests list items"),
            ("Text to test card", "Text to test card"),
            ("", ""),
            (
                """![](assets/images/icons/content/hypotheses.svg#icon-top)""",
                "![](assets/images/icons/content/hypotheses.svg#icon-top)",
            ),
            ("""Code block: ```python print(1)```""", "Code block: ```python print(1)```"),
            ("""[Example page](/test_page)""", "[Example page](/test_page)"),
        ],
    )
    def test_markdown_creation_build(self, test_text, expected):
        card = vm.Card(text=test_text, id="id_valid")
        card = card.build()
        card_markdown = card["id_valid_text"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected

    def test_button_creation_build(self, href="https://www.google.de/"):
        card = vm.Card(text="Test", href=href, id="test_href")
        card = card.build()
        button = card["test_href_button"]

        assert isinstance(button, dbc.Button)
        assert button.href == href

    @pytest.mark.parametrize(
        "test_text, expected",
        [
            ("""<p>Hello </p>""", "<p>Hello </p>"),  # html will not be evaluated but converted to string
            (12345, "12345"),
            ("""$$ \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi)}$$""", "$$ \\frac{1}{(\\sqrt{\\phi \\sqrt{5}}-\\phi)}$$"),
        ],
    )
    def test_markdown_build_invalid(self, test_text, expected):
        card = vm.Card(text=test_text, id="test_id")
        card = card.build()
        card_markdown = card["test_id_text"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected
