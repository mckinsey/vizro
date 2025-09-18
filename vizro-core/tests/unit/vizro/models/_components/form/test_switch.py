"""Unit tests for Switch."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html

import vizro.models as vm


class TestSwitchInstantiation:
    """Tests model instantiation."""

    def test_create_switch_mandatory_only(self):
        switch = vm.Switch()

        assert hasattr(switch, "id")
        assert switch.type == "switch"
        assert switch.value is False
        assert switch.title == ""
        assert switch.actions == []
        assert switch._action_triggers == {"__default__": f"{switch.id}.value"}
        assert switch._action_outputs == {"__default__": f"{switch.id}.value"}
        assert switch._action_inputs == {"__default__": f"{switch.id}.value"}

    def test_create_text_area_mandatory_and_optional(self):
        switch = vm.Switch(
            id="switch-id",
            value=True,
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )

        assert switch.id == "switch-id"
        assert switch.type == "switch"
        assert switch.value is True
        assert switch.title == "Title"
        assert switch.actions == []
        assert isinstance(switch.description, vm.Tooltip)
        assert switch._action_triggers == {"__default__": "switch-id.value"}
        assert switch._action_outputs == {
            "__default__": "switch-id.value",
            "title": "switch-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert switch._action_inputs == {"__default__": "switch-id.value"}

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            ("true", True),
            ("false", False),
        ],
    )
    def test_pydantic_bool_conversion(self, input_value, expected_value):
        switch = vm.Switch(value=input_value)
        assert switch.value is expected_value
        assert isinstance(switch.value, bool)

    def test_switch_trigger(self, identity_action_function):
        switch = vm.Switch(id="switch-id", actions=[vm.Action(function=identity_action_function())])
        [action] = switch.actions
        assert action._trigger == "switch-id.value"


class TestSwitchBuild:
    """Tests model build method."""

    def test_switch_build(self):
        switch = vm.Switch(value=True, title="Show active").build()

        expected_switch = dbc.Switch(
            value=True, label=[html.Span(children="Show active"), None], persistence=True, persistence_type="session"
        )
        assert_component_equal(switch, expected_switch, keys_to_strip={"id"})

    def test_switch_build_with_description(self):
        """Test that description arguments correctly builds icon and tooltip."""
        switch = vm.Switch(
            value=True,
            title="Show active",
            description=vm.Tooltip(text="Test description", icon="info", id="info"),
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

        expected_switch = dbc.Switch(
            value=True,
            label=[html.Span(children="Show active"), *expected_description],
            persistence=True,
            persistence_type="session",
        )
        assert_component_equal(switch, expected_switch, keys_to_strip={"id"})
