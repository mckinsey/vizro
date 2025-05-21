"""Unit tests for UserInput."""

import dash_bootstrap_components as dbc
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm
from vizro.models._components.form._user_input import UserInput


class TestUserInputInstantiation:
    """Tests model instantiation."""

    def test_create_user_input_mandatory_only(self):
        user_input = UserInput()

        assert hasattr(user_input, "id")
        assert user_input.type == "user_input"
        assert user_input.title == ""
        assert user_input.placeholder == ""
        assert user_input.actions == []
        assert user_input._action_outputs == {"__default__": f"{user_input.id}.value"}
        assert user_input._action_inputs == {"__default__": f"{user_input.id}.value"}

    def test_create_user_input_mandatory_and_optional(self):
        user_input = UserInput(
            id="user-input-id",
            title="Title",
            placeholder="Placeholder",
            description="Test description",
        )

        assert user_input.id == "user-input-id"
        assert user_input.type == "user_input"
        assert user_input.title == "Title"
        assert user_input.placeholder == "Placeholder"
        assert user_input.actions == []
        assert user_input._action_outputs == {
            "__default__": f"{user_input.id}.value",
            "title": f"{user_input.id}_title.children",
            "description": f"{user_input.description.id}-text.children",
        }
        assert user_input._action_inputs == {"__default__": f"{user_input.id}.value"}


class TestUserInputBuild:
    """Tests model build method."""

    def test_user_input_build(self):
        user_input = UserInput(id="user-input-id", title="Title", placeholder="Placeholder").build()
        expected_user_input = html.Div(
            [
                dbc.Label([html.Span("Title", id="user-input-id_title"), None], html_for="user-input-id"),
                dbc.Input(
                    id="user-input-id",
                    placeholder="Placeholder",
                    type="text",
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ]
        )
        assert_component_equal(user_input, expected_user_input)

    def test_user_input_build_with_description(self):
        user_input = UserInput(
            id="user-input-id",
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

        expected_user_input = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="user-input-id_title"), *expected_description],
                    html_for="user-input-id",
                ),
                dbc.Input(
                    id="user-input-id",
                    placeholder="Placeholder",
                    type="text",
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                ),
            ]
        )
        assert_component_equal(user_input, expected_user_input)
