"""Unit tests for vizro.models.Markdown."""

import pytest
from asserts import assert_component_equal
from dash import dcc

import vizro.models as vm


class TestMarkdownInstantiation:
    """Tests model instantiation."""

    def test_create_markdown_mandatory_only(self):
        markdown = vm.Markdown(text="Text to test markdown")

        assert hasattr(markdown, "id")
        assert markdown.type == "markdown"
        assert markdown.text == "Text to test markdown"

    @pytest.mark.parametrize("id, text", [("id_1", "Text to test markdown"), ("id_2", "Test")])
    def test_create_card_mandatory_and_optional(self, id, text):
        markdown = vm.Markdown(id=id, text=text)

        assert markdown.id == id
        assert markdown.type == "markdown"
        assert markdown.text == text


class TestBuildMethod:
    """Tests build method."""

    def test_markdown_build(self):
        markdown = vm.Markdown(id="markdown_id", text="Test")
        markdown = markdown.build()

        expected_markdown = dcc.Markdown(
            id="markdown_id",
            children="Test",
            dangerously_allow_html=False,
        )

        assert_component_equal(markdown, expected_markdown)

    def test_markdown_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        markdown = vm.Markdown(id="markdown_id", text="Test", extra={"className": "bg-primary p-1 mt-2 text-center h2"})
        markdown = markdown.build()

        expected_markdown = dcc.Markdown(
            id="markdown_id",
            children="Test",
            dangerously_allow_html=False,
            className="bg-primary p-1 mt-2 text-center h2",
        )

        assert_component_equal(markdown, expected_markdown)

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
                """![](assets/images/icons/content/hypotheses.svg)""",
                "![](assets/images/icons/content/hypotheses.svg)",
            ),
            ("""Code block: ```python print(1)```""", "Code block: ```python print(1)```"),
            ("""[Example page](/test_page)""", "[Example page](/test_page)"),
        ],
    )
    def test_markdown_text(self, test_text, expected):
        markdown = vm.Markdown(id="id_valid", text=test_text)
        markdown = markdown.build()

        assert markdown.children == expected
