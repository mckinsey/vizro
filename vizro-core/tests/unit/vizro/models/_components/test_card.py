"""Unit tests for vizro.models.Card."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestCardInstantiation:
    """Tests model instantiation."""

    def test_create_card_mandatory_only(self):
        card = vm.Card(text="Text to test card")

        assert hasattr(card, "id")
        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.href == ""


    def test_create_card_mandatory_and_optional(self):
        card = vm.Card(text="Text to test card", id="card-id", href="Page 1")

        assert card.id == "card-id"
        assert card.type == "card"
        assert card.text == "Text to test card"
        assert card.href == "/page-1"

    def test_mandatory_text_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Card()

    def test_none_as_text(self):
        with pytest.raises(ValidationError, match="none is not an allowed value"):
            vm.Card(text=None)

    @pytest.mark.parametrize(
        "test_href, expected",
        [
            ("", ""),
            ("/this path works", "/this-path-works"),
            ("/this-path-works", "/this-path-works"),
            ("this path works", "/this-path-works"),
            ("this-path-works", "/this-path-works"),
            ("this_path_works", "/this_path_works"),
            ("this/path/works", "/this/path/works"),
            ("2147abc", "/2147abc"),
            ("https://google.com", "https://google.com"),
            ("http://google.com", "http://google.com"),
            # Note: www.google.com is not considered an absolute path (from the urlparse function and the dbc.NavLink)
            # and will therefore be converted.
            ("www.google.com", "/wwwgooglecom"),
        ],
    )
    def test_set_href_validator(self, test_href, expected):
        card = vm.Card(text="Some Text", href =test_href)
        assert card.href == expected

class TestBuildMethod:
    """Tests build method."""

    def test_card_build(self):
        card = vm.Card(id="card_id", text="Hello", href="https://www.google.com")
        card = card.build()

        expected_card = html.Div(
            dbc.NavLink(
                dcc.Markdown("Hello", className="card_text", dangerously_allow_html=False, id="card_id"),
                href="https://www.google.com",
                className="card-link",
            ),
            className="nav_card_container",
            id="card_id_outer",
        )

        assert_component_equal(card, expected_card)

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
    def test_markdown_setting(self, test_text, expected):
        card = vm.Card(text=test_text, id="id_valid")
        card = card.build()
        card_markdown = card["id_valid"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected

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
        card_markdown = card["test_id"]

        assert isinstance(card_markdown, dcc.Markdown)
        assert card_markdown.dangerously_allow_html is False
        assert card_markdown.children == expected
