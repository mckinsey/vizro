"""Unit tests for UserInput."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

from vizro.models._components.form._user_input import UserInput


class TestUserInputInstantiation:
    """Tests model instantiation."""

    def test_create_user_input_mandatory_only(self):
        user_input = UserInput()

        assert hasattr(user_input, "id")
        assert user_input.type == "user_input"
        assert user_input.title == ""
        assert user_input.placeholder == ""
        assert user_input.input_type == "text"
        assert user_input.actions == []

    def test_create_user_input_mandatory_and_optional(self):
        user_input = UserInput(title="Title", placeholder="Placeholder", input_type="number", id="user-input-id")

        assert user_input.id == "user-input-id"
        assert user_input.type == "user_input"
        assert user_input.title == "Title"
        assert user_input.placeholder == "Placeholder"
        assert user_input.input_type == "number"
        assert user_input.actions == []

    @pytest.mark.parametrize("test_input_type", ["text", "number", "password", "email", "search", "tel", "url"])
    def test_create_user_input_valid_input_type(self, test_input_type):
        user_input = UserInput(input_type=test_input_type)

        assert hasattr(user_input, "id")
        assert user_input.type == "user_input"
        assert user_input.title == ""
        assert user_input.placeholder == ""
        assert user_input.input_type == test_input_type
        assert user_input.actions == []

    @pytest.mark.parametrize("test_input_type", ["range", "hidden"])
    def test_create_user_input_invalid_input_type(self, test_input_type):
        with pytest.raises(
            ValidationError,
            match="unexpected value; permitted: 'text', 'number', 'password', 'email', 'search', 'tel', 'url'",
        ):
            UserInput(input_type=test_input_type)


class TestUserInputBuild:
    """Tests model build method."""

    def test_user_input_build(self):
        user_input = UserInput(
            title="Title", placeholder="Placeholder", input_type="number", id="user-input-id"
        ).build()
        expected_user_input = html.Div(
            [
                html.Label("Title", htmlFor="user-input-id"),
                dbc.Input(
                    id="user-input-id",
                    placeholder="Placeholder",
                    type="number",
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
