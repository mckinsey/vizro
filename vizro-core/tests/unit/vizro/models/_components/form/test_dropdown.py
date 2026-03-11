"""Unit tests for vizro.models.Dropdown."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

from vizro.models import Tooltip
from vizro.models._action._action import Action
from vizro.models._components.form import Dropdown


class TestDropdownInstantiation:
    """Tests model instantiation."""

    def test_create_dropdown_mandatory_only(self):
        dropdown = Dropdown()

        assert hasattr(dropdown, "id")
        assert dropdown.type == "dropdown"
        assert dropdown.options == []
        assert dropdown.value is None
        assert dropdown.multi is True
        assert dropdown.title == ""
        assert dropdown.variant == "filled"
        assert dropdown.description is None
        assert dropdown.actions == []
        assert dropdown._action_triggers == {"__default__": f"{dropdown.id}.value"}
        assert dropdown._action_outputs == {"__default__": f"{dropdown.id}.value"}
        assert dropdown._action_inputs == {"__default__": f"{dropdown.id}.value"}

    def test_create_dropdown_mandatory_and_optional(self):
        dropdown = Dropdown(
            id="dropdown-id",
            options=["A", "B", "C"],
            value="A",
            multi=False,
            title="Title",
            variant="plain",
            description=Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )

        assert dropdown.id == "dropdown-id"
        assert dropdown.type == "dropdown"
        assert dropdown.options == ["A", "B", "C"]
        assert dropdown.value == "A"
        assert dropdown.multi is False
        assert dropdown.title == "Title"
        assert dropdown.variant == "plain"
        assert dropdown.actions == []
        assert isinstance(dropdown.description, Tooltip)
        assert dropdown._action_triggers == {"__default__": "dropdown-id.value"}
        assert dropdown._action_outputs == {
            "__default__": "dropdown-id.value",
            "title": "dropdown-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert dropdown._action_inputs == {"__default__": "dropdown-id.value"}

    @pytest.mark.parametrize(
        "test_options, expected",
        [
            (["A", "B", "C"], ["A", "B", "C"]),
            ([1, 2, 3], [1.0, 2.0, 3.0]),
            ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]),
            ([True, False, True], [True, False, True]),
            (
                [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}],
                [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}],
            ),
            (
                [{"label": "New York", "value": "NYC"}, {"label": "Berlin", "value": "BER"}],
                [{"label": "New York", "value": "NYC"}, {"label": "Berlin", "value": "BER"}],
            ),
            (
                [{"label": "True", "value": True}, {"label": "False", "value": False}],
                [{"label": "True", "value": True}, {"label": "False", "value": False}],
            ),
        ],
    )
    def test_create_dropdown_valid_options(self, test_options, expected):
        dropdown = Dropdown(options=test_options)

        assert hasattr(dropdown, "id")
        assert dropdown.type == "dropdown"
        assert dropdown.options == expected
        assert dropdown.value is None
        assert dropdown.multi is True
        assert dropdown.title == ""
        assert dropdown.actions == []

    @pytest.mark.parametrize("test_options", [1, "A", True, 1.0, [True, 2.0, 1.0, "A", "B"]])
    def test_create_dropdown_invalid_options_type(self, test_options):
        with pytest.raises(ValidationError, match="Input should be a valid"):
            Dropdown(options=test_options)

    def test_create_dropdown_invalid_options_dict(self):
        with pytest.raises(ValidationError, match="Field required"):
            Dropdown(options=[{"hello": "A", "world": "A"}, {"hello": "B", "world": "B"}])

    def test_validate_options_dict_produces_clean_errors(self):
        """Test that _validate_options produces 2 clean errors instead of 8 messy ones."""
        with pytest.raises(ValidationError) as exc_info:
            Dropdown(options=[{"hello": "A", "world": "A"}])

        # With validator: 2 errors (label, value). Without: 8 errors with nested paths.
        assert len(exc_info.value.errors()) == 2

    @pytest.mark.parametrize(
        "test_value, options, multi",
        [
            # Single default value with multi=False
            ("A", ["A", "B", "C"], False),
            (1, [1, 2, 3], False),
            (1.0, [1.0, 2.0, 3.0], False),
            (False, [True, False], False),
            ("A", [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}], False),
            # Single default value with multi=True
            ("A", ["A", "B", "C"], True),
            (1, [1, 2, 3], True),
            (1.0, [1.0, 2.0, 3.0], True),
            (False, [True, False], True),
            ("A", [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}], True),
            # List of default values with multi=True
            (["A", "B"], ["A", "B", "C"], True),
            ([1, 2], [1, 2, 3], True),
            ([1.0, 2.0], [1.0, 2.0, 3.0], True),
            ([False, True], [True, False], True),
            (["A", "B"], [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}], True),
        ],
    )
    def test_create_dropdown_valid_value(self, test_value, options, multi):
        dropdown = Dropdown(options=options, value=test_value, multi=multi)

        assert hasattr(dropdown, "id")
        assert dropdown.type == "dropdown"
        assert dropdown.value == test_value
        assert dropdown.multi == multi
        assert dropdown.title == ""
        assert dropdown.actions == []

    @pytest.mark.parametrize(
        "test_value, options",
        [
            (5, ["A", "B", "C"]),
            (5, [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            ("D", ["A", "B", "C"]),
            ("D", [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
            (True, ["A", "B", "C"]),
            (True, [{"label": "A", "value": "A"}, {"label": "B", "value": "B"}]),
        ],
    )
    def test_create_dropdown_invalid_value(self, test_value, options):
        with pytest.raises(ValidationError, match=r"Please provide a valid value from `options`."):
            Dropdown(value=test_value, options=options)

    def test_create_dropdown_invalid_multi(self):
        with pytest.raises(ValidationError, match=r"Please set multi=True if providing a list of default values."):
            Dropdown(value=[1, 2], multi=False, options=[1, 2, 3, 4, 5])

    def test_dropdown_trigger(self, identity_action_function):
        dropdown = Dropdown(id="dropdown-id", actions=[Action(function=identity_action_function())])
        [action] = dropdown.actions
        assert action._trigger == "dropdown-id.value"


class TestDropdownBuild:
    """Tests model build method."""

    def test_dropdown_build(self):
        dropdown = Dropdown(id="dropdown_id", options=["A", "B", "C"], multi=False, title="Title").build()
        expected_dropdown = html.Div(
            [
                dbc.Label([html.Span("Title", id="dropdown_id_title"), None], html_for="dropdown_id"),
                dcc.Dropdown(
                    id="dropdown_id",
                    options=[{"label": "A", "value": "A"}, {"label": "B", "value": "B"}, {"label": "C", "value": "C"}],
                    value="A",
                    multi=False,
                    clearable=False,
                    placeholder="Select option",
                    persistence=True,
                    persistence_type="session",
                    className="",
                ),
            ]
        )

        assert_component_equal(dropdown, expected_dropdown)

    def test_dropdown_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        dropdown = Dropdown(
            options=["A", "B", "C"],
            title="Title",
            id="dropdown_id",
            multi=False,
            extra={
                "clearable": True,
                "id": "overridden_id",
            },
        ).build()
        expected_dropdown = html.Div(
            [
                dbc.Label([html.Span("Title", id="dropdown_id_title"), None], html_for="dropdown_id"),
                dcc.Dropdown(
                    id="overridden_id",
                    options=[
                        {"label": "A", "value": "A"},
                        {"label": "B", "value": "B"},
                        {"label": "C", "value": "C"},
                    ],
                    value="A",
                    multi=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    className="",
                    clearable=True,
                ),
            ]
        )

        assert_component_equal(dropdown, expected_dropdown)

    def test_dropdown_with_description(self):
        dropdown = Dropdown(
            options=["A", "B", "C"],
            multi=False,
            title="Title",
            id="dropdown_id",
            description=Tooltip(text="Test description", icon="Info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        expected_dropdown = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="dropdown_id_title"), *expected_description],
                    html_for="dropdown_id",
                ),
                dcc.Dropdown(
                    id="dropdown_id",
                    options=[
                        {"label": "A", "value": "A"},
                        {"label": "B", "value": "B"},
                        {"label": "C", "value": "C"},
                    ],
                    value="A",
                    multi=False,
                    clearable=False,
                    persistence=True,
                    persistence_type="session",
                    placeholder="Select option",
                    className="",
                ),
            ]
        )

        assert_component_equal(dropdown, expected_dropdown)

    def test_dropdown_build_with_variant(self):
        dropdown = Dropdown(
            id="dropdown_id", options=["A", "B", "C"], multi=False, title="Title", variant="plain"
        ).build()
        expected_dropdown = html.Div(
            [
                dbc.Label([html.Span("Title", id="dropdown_id_title"), None], html_for="dropdown_id"),
                dcc.Dropdown(
                    id="dropdown_id",
                    options=[{"label": "A", "value": "A"}, {"label": "B", "value": "B"}, {"label": "C", "value": "C"}],
                    value="A",
                    multi=False,
                    clearable=False,
                    placeholder="Select option",
                    persistence=True,
                    persistence_type="session",
                    className="dropdown-plain",
                ),
            ]
        )

        assert_component_equal(dropdown, expected_dropdown)
