"""Unit tests for TimePicker."""

from datetime import time

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pytest
import vizro_dash_components as vdc
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


class TestTimePickerInstantiation:
    """Tests model instantiation."""

    def test_create_timepicker_mandatory(self):
        time_picker = vm.TimePicker()

        assert hasattr(time_picker, "id")
        assert time_picker.type == "time_picker"
        assert time_picker.value is None
        assert time_picker.title == ""
        assert time_picker.description is None
        assert time_picker.actions == []
        assert time_picker.range is True
        # range=True uses dcc.Store as a proxy, so its property is "data".
        assert time_picker._action_triggers == {"__default__": f"{time_picker.id}.data"}
        assert time_picker._action_outputs == {"__default__": f"{time_picker.id}.data"}
        assert time_picker._action_inputs == {"__default__": f"{time_picker.id}.data"}

    def test_create_timepicker_mandatory_and_optional(self):
        time_picker = vm.TimePicker(
            id="time-picker-id",
            # Mix HH:MM and HH:MM:SS string formats to confirm both are accepted and preserved as-is.
            value=["09:00", "17:00:30"],
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            range=True,
        )

        assert time_picker.id == "time-picker-id"
        assert time_picker.type == "time_picker"
        assert time_picker.value == ["09:00", "17:00:30"]
        assert all(isinstance(v, str) for v in time_picker.value)
        assert time_picker.title == "Title"
        assert time_picker.actions == []
        assert time_picker.range is True
        assert isinstance(time_picker.description, vm.Tooltip)
        assert time_picker._action_triggers == {"__default__": "time-picker-id.data"}
        assert time_picker._action_outputs == {
            "__default__": "time-picker-id.data",
            "title": "time-picker-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert time_picker._action_inputs == {"__default__": "time-picker-id.data"}

    def test_create_timepicker_single_mode(self):
        """Single-mode TimePicker (range=False) is backed by the dmc input directly, so its property is `value`."""
        time_picker = vm.TimePicker(id="tp-single", range=False, value="10:30")

        assert time_picker.range is False
        assert time_picker.value == "10:30"
        assert time_picker._action_triggers == {"__default__": "tp-single.value"}
        assert time_picker._action_outputs == {"__default__": "tp-single.value"}
        assert time_picker._action_inputs == {"__default__": "tp-single.value"}

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        time_picker = vm.TimePicker(title=title)

        assert time_picker.title == str(title)

    def test_time_picker_trigger_range(self, identity_action_function):
        """Range-mode trigger fires on the dcc.Store proxy's `data` property."""
        time_picker = vm.TimePicker(id="tp-range", actions=[vm.Action(function=identity_action_function())])
        [action] = time_picker.actions
        assert action._trigger == "tp-range.data"

    def test_time_picker_trigger_single(self, identity_action_function):
        """Single-mode trigger fires on the dmc.TimePicker's own `value` property."""
        time_picker = vm.TimePicker(
            id="tp-single", range=False, actions=[vm.Action(function=identity_action_function())]
        )
        [action] = time_picker.actions
        assert action._trigger == "tp-single.value"

    @pytest.mark.parametrize(
        "value",
        [
            ["09:00", "17:00"],
            ["09:00:30", "17:00:30"],
            [time(9, 0), time(17, 0)],
            ["09:00", time(17, 0)],  # Mixed string/time list is allowed by `list[time | str]`.
        ],
    )
    def test_validate_range_true_value_valid(self, value):
        time_picker = vm.TimePicker(range=True, value=value)
        assert time_picker.value == value

    @pytest.mark.parametrize(
        "value",
        [
            "09:00",
            "09:00:30",
            time(9, 0),
        ],
    )
    def test_validate_range_false_value_valid(self, value):
        time_picker = vm.TimePicker(range=False, value=value)
        assert time_picker.value == value

    @pytest.mark.parametrize(
        "range, value",
        [
            # range=True needs a list of two values.
            (True, "09:00"),
            (True, ["09:00"]),
            (True, time(9, 0)),
            # range=False needs a single value.
            (False, ["09:00"]),
            (False, ["09:00", "17:00"]),
        ],
    )
    def test_validate_timepicker_range_invalid(self, range, value):
        with pytest.raises(ValidationError):
            vm.TimePicker(range=range, value=value)

    @pytest.mark.parametrize(
        "range, value",
        [
            # Single-mode invalid strings.
            (False, "10"),
            (False, "10:60"),
            (False, "10:30:60"),
            (False, "9:30 AM"),
            (False, "not-a-time"),
            (False, "25:00"),
            # Range-mode invalid strings (one bad value is enough).
            (True, ["09:00", "25:00"]),
            (True, ["bad", "17:00"]),
            (True, ["09:00:99", "17:00"]),
        ],
    )
    def test_validate_timepicker_value_invalid_format(self, range, value):
        """String values must parse as HH:MM or HH:MM:SS."""
        with pytest.raises(ValidationError, match="Invalid time string"):
            vm.TimePicker(range=range, value=value)

    def test_timepicker_value_string_not_coerced_to_time(self):
        """String values stay as strings — they must not be coerced to `datetime.time`."""
        time_picker = vm.TimePicker(range=True, value=["09:00", "17:00:30"])
        assert time_picker.value == ["09:00", "17:00:30"]
        assert all(isinstance(v, str) for v in time_picker.value)

        time_picker = vm.TimePicker(range=False, value="09:00")
        assert time_picker.value == "09:00"
        assert isinstance(time_picker.value, str)


class TestBuildMethod:
    def test_timepicker_range_build(self):
        time_picker = vm.TimePicker(id="timepicker_id", range=True, value=["09:00", "17:00"], title="Title").build()

        expected_timepicker = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="timepicker_id_title"), None], html_for="timepicker_id-start"),
                html.Div(
                    children=[
                        dmc.TimePicker(id="timepicker_id-start", value="09:00", label="From:", debounce=True),
                        dmc.TimePicker(id="timepicker_id-end", value="17:00", label="To:", debounce=True),
                    ],
                    style={"display": "flex", "gap": "8px"},
                ),
                dcc.Store(id="timepicker_id", data=["09:00", "17:00"], storage_type="session"),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)

    def test_timepicker_single_build(self):
        time_picker = vm.TimePicker(id="timepicker_id", range=False, value="09:00", title="Title").build()

        expected_timepicker = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="timepicker_id_title"), None], html_for="timepicker_id"),
                dmc.TimePicker(id="timepicker_id", value="09:00", debounce=True),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)

    def test_timepicker_build_no_title(self):
        """When no title is set, the label is None."""
        time_picker = vm.TimePicker(id="timepicker_id", range=False, value="10:30").build()

        expected_timepicker = html.Div(
            children=[
                None,
                dmc.TimePicker(id="timepicker_id", value="10:30", debounce=True),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)

    def test_timepicker_build_with_description(self):
        time_picker = vm.TimePicker(
            id="timepicker_id",
            range=False,
            value="10:30",
            title="Title",
            description=vm.Tooltip(text="Test description", icon="Info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=vdc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]
        expected_timepicker = html.Div(
            children=[
                dbc.Label(
                    [html.Span("Title", id="timepicker_id_title"), *expected_description],
                    html_for="timepicker_id",
                ),
                dmc.TimePicker(id="timepicker_id", value="10:30", debounce=True),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)

    def test_range_timepicker_build_with_extra(self):
        """Extra keyword arguments override defaults for both pickers in range mode."""
        time_picker = vm.TimePicker(
            id="timepicker_id",
            range=True,
            value=["09:00", "17:00"],
            title="Title",
            extra={"withDropdown": True, "clearable": True},
        ).build()

        expected_timepicker = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="timepicker_id_title"), None], html_for="timepicker_id-start"),
                html.Div(
                    children=[
                        dmc.TimePicker(
                            id="timepicker_id-start",
                            value="09:00",
                            label="From:",
                            debounce=True,
                            withDropdown=True,
                            clearable=True,
                        ),
                        dmc.TimePicker(
                            id="timepicker_id-end",
                            value="17:00",
                            label="To:",
                            debounce=True,
                            withDropdown=True,
                            clearable=True,
                        ),
                    ],
                    style={"display": "flex", "gap": "8px"},
                ),
                dcc.Store(id="timepicker_id", data=["09:00", "17:00"], storage_type="session"),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)

    def test_single_timepicker_build_with_extra(self):
        """Extra keyword arguments override defaults in single mode."""
        time_picker = vm.TimePicker(
            id="timepicker_id",
            range=False,
            value="10:30",
            title="Title",
            extra={"withDropdown": True, "clearable": True},
        ).build()

        expected_timepicker = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="timepicker_id_title"), None], html_for="timepicker_id"),
                dmc.TimePicker(
                    id="timepicker_id",
                    value="10:30",
                    debounce=True,
                    withDropdown=True,
                    clearable=True,
                ),
            ]
        )
        assert_component_equal(time_picker, expected_timepicker)
