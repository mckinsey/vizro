"""Unit tests for vizro.models.Text."""

from asserts import assert_component_equal
from dash import dcc

import vizro.models as vm


class TestTextInstantiation:
    """Tests model instantiation."""

    def test_create_text_mandatory_only(self):
        text = vm.Text(text="Text to test")

        assert hasattr(text, "id")
        assert text.type == "text"
        assert text.text == "Text to test"
        assert text._action_outputs == {
            "__default__": f"{text.id}.children",
            "text": f"{text.id}.children",
        }

    def test_create_text_mandatory_and_optional(self):
        text = vm.Text(id="text-id", text="Text to test")

        assert text.id == "text-id"
        assert text.type == "text"
        assert text.text == "Text to test"
        assert text._action_outputs == {
            "__default__": "text-id.children",
            "text": "text-id.children",
        }


class TestBuildMethod:
    """Tests build method."""

    def test_text_build(self):
        text = vm.Text(id="text_id", text="Test")
        text = text.build()

        expected = dcc.Markdown(
            id="text_id",
            children="Test",
            dangerously_allow_html=False,
        )

        assert_component_equal(text, expected)

    def test_text_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        text = vm.Text(id="text_id", text="Test", extra={"className": "bg-primary p-1 mt-2 text-center h2"})
        text = text.build()

        expected = dcc.Markdown(
            id="text_id",
            children="Test",
            dangerously_allow_html=False,
            className="bg-primary p-1 mt-2 text-center h2",
        )

        assert_component_equal(text, expected)
