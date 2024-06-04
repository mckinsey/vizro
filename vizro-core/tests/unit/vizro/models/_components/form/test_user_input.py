"""Unit tests for UserInput."""

import dash_bootstrap_components as dbc
from asserts import assert_component_equal
from dash import html
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

    def test_create_user_input_mandatory_and_optional(self):
        user_input = UserInput(id="user-input-id", title="Title", placeholder="Placeholder")

        assert user_input.id == "user-input-id"
        assert user_input.type == "user_input"
        assert user_input.title == "Title"
        assert user_input.placeholder == "Placeholder"
        assert user_input.actions == []


class TestUserInputBuild:
    """Tests model build method."""

    def test_user_input_build(self):
        user_input = UserInput(id="user-input-id", title="Title", placeholder="Placeholder").build()
        expected_user_input = html.Div(
            [
                dbc.Label("Title", html_for="user-input-id"),
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
