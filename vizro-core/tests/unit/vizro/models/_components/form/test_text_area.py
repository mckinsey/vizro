"""Unit tests for TextArea."""

import dash_bootstrap_components as dbc
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
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
        assert text_area._action_outputs == {"__default__": f"{text_area.id}.value"}
        assert text_area._action_inputs == {"__default__": f"{text_area.id}.value"}

    def test_create_text_area_mandatory_and_optional(self):
        text_area = TextArea(
            id="text-area-id",
            title="Title",
            placeholder="Placeholder",
            description="Test description",
        )

        assert text_area.id == "text-area-id"
        assert text_area.type == "text_area"
        assert text_area.title == "Title"
        assert text_area.placeholder == "Placeholder"
        assert text_area.actions == []
        assert text_area._action_outputs == {
            "__default__": f"{text_area.id}.value",
            "title": f"{text_area.id}_title.children",
            "description": f"{text_area.description.id}-text.children",
        }
        assert text_area._action_inputs == {"__default__": f"{text_area.id}.value"}


class TestTextAreaBuild:
    """Tests model build method."""

    def test_text_area_build(self):
        text_area = TextArea(id="text-area-id", title="Title", placeholder="Placeholder").build()
        expected_text_area = html.Div(
            [
                dbc.Label([html.Span("Title", id="text-area-id_title"), None], html_for="text-area-id"),
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

    def test_text_area_build_with_description(self):
        text_area = TextArea(
            id="text-area-id",
            title="Title",
            description=vm.Tooltip(text="Tooltip test", icon="info", id="info"),
            placeholder="Placeholder",
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected_text_area = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="text-area-id_title"), *expected_description],
                    html_for="text-area-id",
                ),
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
