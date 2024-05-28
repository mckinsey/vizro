"""Unit tests for TextArea."""

import dash_bootstrap_components as dbc
from asserts import assert_component_equal
from dash import html
from vizro.models._components.form._text_area import TextArea


class TestTextAreaInstantiation:
    """Tests model instantiation."""

    def test_create_text_area_mandatory_only(self):
        text_area = TextArea()

        assert hasattr(text_area, "id")
        assert text_area.type == "text_area"
        assert text_area.title == ""
        assert text_area.placeholder == ""
        assert text_area.actions == []

    def test_create_text_area_mandatory_and_optional(self):
        text_area = TextArea(id="text-area-id", title="Title", placeholder="Placeholder")

        assert text_area.id == "text-area-id"
        assert text_area.type == "text_area"
        assert text_area.title == "Title"
        assert text_area.placeholder == "Placeholder"
        assert text_area.actions == []


class TestUserInputBuild:
    """Tests model build method."""

    def test_text_area_build(self):
        text_area = TextArea(id="text-area-id", title="Title", placeholder="Placeholder").build()
        expected_text_area = html.Div(
            [
                dbc.Label("Title", html_for="text-area-id"),
                dbc.Textarea(
                    id="text-area-id",
                    placeholder="Placeholder",
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ]
        )
        assert_component_equal(text_area, expected_text_area)
