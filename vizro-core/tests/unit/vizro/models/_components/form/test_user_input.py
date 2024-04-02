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
        user_input = UserInput(title="Title", placeholder="Placeholder", id="user-input-id")

        assert user_input.id == "user-input-id"
        assert user_input.type == "user_input"
        assert user_input.title == "Title"
        assert user_input.placeholder == "Placeholder"
        assert user_input.actions == []


class TestUserInputBuild:
    """Tests model build method."""

    def test_user_input_build(self):
        user_input = UserInput(title="Title", placeholder="Placeholder", id="user-input-id").build()
        expected_user_input = html.Div(
            [
                html.Label("Title", htmlFor="user-input-id"),
                dbc.Input(
                    id="user-input-id",
                    placeholder="Placeholder",
                    type="text",
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                    className="user_input",
                ),
            ],
            className="input-container",
            id="user-input-id_outer",
        )
        assert_component_equal(user_input, expected_user_input)
