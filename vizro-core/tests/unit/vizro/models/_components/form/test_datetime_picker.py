"""Unit tests for DateTimePicker."""

from datetime import date, datetime

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import pytest
import vizro_dash_components as vdc
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


class TestDateTimePickerInstantiation:
    """Tests model instantiation."""

    def test_create_datetimepicker_mandatory(self):
        datetime_picker = vm.DateTimePicker()

        assert hasattr(datetime_picker, "id")
        assert datetime_picker.type == "datetime_picker"
        assert datetime_picker.min is None
        assert datetime_picker.max is None
        assert datetime_picker.value is None
        assert datetime_picker.title == ""
        assert datetime_picker.description is None
        assert datetime_picker.actions == []
        assert datetime_picker.range is True
        # Both range and single modes use a dcc.Store proxy, so the property is always "data"
        # (unlike TimePicker/DatePicker whose single mode uses "value").
        assert datetime_picker._action_triggers == {"__default__": f"{datetime_picker.id}.data"}
        assert datetime_picker._action_outputs == {"__default__": f"{datetime_picker.id}.data"}
        assert datetime_picker._action_inputs == {"__default__": f"{datetime_picker.id}.data"}

    def test_create_datetimepicker_mandatory_and_optional(self):
        datetime_picker = vm.DateTimePicker(
            id="datetime-picker-id",
            min="2024-01-01",
            max="2024-12-31",
            # Mix THH:MM and HH:MM:SS precision to confirm both are accepted and preserved as-is.
            value=["2024-03-01T09:00", "2024-04-01 17:00:30"],
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            range=True,
        )

        assert datetime_picker.id == "datetime-picker-id"
        assert datetime_picker.type == "datetime_picker"
        assert datetime_picker.min == date(2024, 1, 1)
        assert datetime_picker.max == date(2024, 12, 31)
        assert datetime_picker.value == ["2024-03-01T09:00", "2024-04-01 17:00:30"]
        assert datetime_picker.title == "Title"
        assert datetime_picker.actions == []
        assert datetime_picker.range is True
        assert isinstance(datetime_picker.description, vm.Tooltip)
        assert datetime_picker._action_triggers == {"__default__": "datetime-picker-id.data"}
        assert datetime_picker._action_outputs == {
            "__default__": "datetime-picker-id.data",
            "title": "datetime-picker-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert datetime_picker._action_inputs == {"__default__": "datetime-picker-id.data"}

    def test_create_datetimepicker_single_mode(self):
        """Single-mode DateTimePicker (range=False) still proxies through a dcc.Store, so its property is `data`."""
        datetime_picker = vm.DateTimePicker(id="dtp-single", range=False, value="2024-03-01T10:30")

        assert datetime_picker.range is False
        assert datetime_picker.value == "2024-03-01T10:30"
        assert datetime_picker._action_triggers == {"__default__": "dtp-single.data"}
        assert datetime_picker._action_outputs == {"__default__": "dtp-single.data"}
        assert datetime_picker._action_inputs == {"__default__": "dtp-single.data"}

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        datetime_picker = vm.DateTimePicker(title=title)

        assert datetime_picker.title == str(title)

    def test_datetime_picker_trigger_range(self, identity_action_function):
        """Range-mode trigger fires on the dcc.Store proxy's `data` property."""
        datetime_picker = vm.DateTimePicker(id="dtp-range", actions=[vm.Action(function=identity_action_function())])
        [action] = datetime_picker.actions
        assert action._trigger == "dtp-range.data"

    def test_datetime_picker_trigger_single(self, identity_action_function):
        """Single-mode trigger also fires on the dcc.Store proxy's `data` property."""
        datetime_picker = vm.DateTimePicker(
            id="dtp-single", range=False, actions=[vm.Action(function=identity_action_function())]
        )
        [action] = datetime_picker.actions
        assert action._trigger == "dtp-single.data"

    @pytest.mark.parametrize(
        "min, max, expected_min, expected_max",
        [
            ("2024-01-01", None, date(2024, 1, 1), None),
            (None, "2024-01-01", None, date(2024, 1, 1)),
            ("2024-01-01", "2024-02-01", date(2024, 1, 1), date(2024, 2, 1)),
            # `datetime` objects with a time component are coerced to pure dates: min/max bound the date
            # portion only (the time portion is always the full 00:00-23:59 day).
            (datetime(2024, 1, 1, 10, 10, 10), datetime(2024, 2, 1, 20), date(2024, 1, 1), date(2024, 2, 1)),
            (datetime(2024, 1, 1, 0, 0, 0, 123456), datetime(2024, 2, 1), date(2024, 1, 1), date(2024, 2, 1)),
            # ISO datetime strings with a time part are coerced to date the same way (T and space separators).
            ("2024-01-01T10:00", "2024-02-01T20:00", date(2024, 1, 1), date(2024, 2, 1)),
            ("2024-01-01 10:00", "2024-02-01 20:00", date(2024, 1, 1), date(2024, 2, 1)),
            ("2024-01-01T10:00:30", "2024-02-01T20:00:45", date(2024, 1, 1), date(2024, 2, 1)),
        ],
    )
    def test_valid_min_max(self, min, max, expected_min, expected_max):
        datetime_picker = vm.DateTimePicker(min=min, max=max)

        assert datetime_picker.min == expected_min
        assert datetime_picker.max == expected_max

    def test_validate_max_invalid_min_greater_than_max(self):
        with pytest.raises(
            ValidationError, match=r"Maximum value of selector is required to be larger than minimum value."
        ):
            vm.DateTimePicker(min="2024-02-01", max="2024-01-01")

    def test_validate_min_max_invalid_date_format(self):
        with pytest.raises(ValidationError, match="Input should be a valid date or datetime"):
            vm.DateTimePicker(min="50-50-50", max="50-50-50")

    @pytest.mark.parametrize(
        "range, value",
        [
            # range=True needs a list of two values; a scalar (incl. datetime/Timestamp) must be rejected.
            (True, "2024-01-01T09:00"),
            (True, ["2024-01-01T09:00"]),
            (True, datetime(2024, 1, 1, 9, 0)),
            (True, pd.Timestamp("2024-01-01T09:00")),
            # range=False needs a single value, not a list.
            (False, ["2024-01-01T09:00"]),
            (False, ["2024-01-01T09:00", "2024-02-01T17:00"]),
        ],
    )
    def test_validate_datetimepicker_range_invalid(self, range, value):
        with pytest.raises(ValidationError):
            vm.DateTimePicker(range=range, value=value)

    @pytest.mark.parametrize(
        "value",
        [
            "2024-01-01T09:00",  # T separator, HH:MM
            "2024-01-01T09:00:30",  # T separator, HH:MM:SS
            "2024-01-01 09:00",  # space separator (emitted by Mantine after interaction)
            "2024-01-01 09:00:30",  # space separator, HH:MM:SS
            "2024-01-01",  # date-only (time portion cleared)
        ],
    )
    def test_validate_datetimepicker_value_valid_format(self, value):
        """All accepted ISO date/datetime string shapes pass validation and stay as strings."""
        datetime_picker = vm.DateTimePicker(range=False, value=value)
        assert datetime_picker.value == value
        assert isinstance(datetime_picker.value, str)

    @pytest.mark.parametrize(
        "range, value",
        [
            (False, "2024-01-01T25:00"),  # invalid hour
            (False, "2024-13-01T09:00"),  # invalid month
            (False, "01-01-2024T09:00"),  # wrong date order
            (False, "not-a-datetime"),
            (True, ["2024-01-01T09:00", "2024-01-01T99:00"]),  # one bad value is enough
        ],
    )
    def test_validate_datetimepicker_value_invalid_format(self, range, value):
        """String values must parse as an ISO date or datetime."""
        with pytest.raises(ValidationError, match="Invalid datetime string"):
            vm.DateTimePicker(range=range, value=value)

    def test_datetimepicker_value_string_not_coerced(self):
        """String values stay as strings — they must not be coerced to `datetime` (which would change precision)."""
        datetime_picker = vm.DateTimePicker(range=True, value=["2024-01-01T09:00", "2024-02-01T17:00:30"])
        assert datetime_picker.value == ["2024-01-01T09:00", "2024-02-01T17:00:30"]
        assert all(isinstance(v, str) for v in datetime_picker.value)

    @pytest.mark.parametrize(
        "value, expected",
        [
            # datetime objects (incl. sub-second precision) are normalized to seconds-precision ISO strings,
            # since dmc.TimePicker only renders HH:MM[:SS] — fractional seconds break rendering/round-trips.
            (datetime(2024, 1, 1, 9, 0, 0, 123456), "2024-01-01T09:00:00"),
            (datetime(2024, 1, 1, 9, 0), "2024-01-01T09:00:00"),
            (pd.Timestamp("2024-01-01T09:00:30.999999"), "2024-01-01T09:00:30"),
        ],
    )
    def test_datetimepicker_datetime_value_normalized_to_seconds(self, value, expected):
        datetime_picker = vm.DateTimePicker(range=False, value=value)
        assert datetime_picker.value == expected
        assert isinstance(datetime_picker.value, str)

    def test_datetimepicker_range_datetime_value_normalized_to_seconds(self):
        """Each datetime end of a range is normalized independently to a seconds-precision ISO string."""
        datetime_picker = vm.DateTimePicker(
            range=True,
            value=[datetime(2024, 1, 1, 9, 0, 0, 123456), pd.Timestamp("2024-02-01T17:30:45.999")],
        )
        assert datetime_picker.value == ["2024-01-01T09:00:00", "2024-02-01T17:30:45"]
        assert all(isinstance(v, str) for v in datetime_picker.value)


class TestBuildMethod:
    """Tests the build method for range and single modes."""

    def test_datetimepicker_range_build(self):
        datetime_picker = vm.DateTimePicker(
            id="dtp",
            min="2026-01-01",
            max="2026-12-31",
            range=True,
            # Mixed precision: start has HH:MM, end has HH:MM:SS — both preserved through the split.
            value=["2026-01-01T09:00", "2026-06-15T14:30:15"],
            title="Title",
        ).build()

        date_defaults = {
            "minDate": date(2026, 1, 1),
            "maxDate": date(2026, 12, 31),
            "valueFormat": "MMM D, YYYY",
            "persistence": True,
            "persistence_type": "session",
            "withCellSpacing": False,
            "placeholder": "Pick a date",
        }
        time_defaults = {"debounce": True, "persistence": True, "persistence_type": "session"}

        expected = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="dtp_title"), None], html_for="dtp-date-start"),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div("From", className="vizro_datetime_picker_label"),
                                html.Div(
                                    children=[
                                        dmc.DatePickerInput(
                                            id="dtp-date-start", type="default", value="2026-01-01", **date_defaults
                                        ),
                                        dmc.TimePicker(id="dtp-time-start", value="09:00", **time_defaults),
                                    ],
                                    className="vizro_datetime_picker_single",
                                ),
                            ],
                            className="vizro_datetime_picker_range_item",
                        ),
                        html.Div(
                            children=[
                                html.Div("To", className="vizro_datetime_picker_label"),
                                html.Div(
                                    children=[
                                        dmc.DatePickerInput(
                                            id="dtp-date-end", type="default", value="2026-06-15", **date_defaults
                                        ),
                                        dmc.TimePicker(id="dtp-time-end", value="14:30:15", **time_defaults),
                                    ],
                                    className="vizro_datetime_picker_single",
                                ),
                            ],
                            className="vizro_datetime_picker_range_item",
                        ),
                    ],
                    className="vizro_datetime_picker_range",
                ),
                dcc.Store(id="dtp", data=["2026-01-01T09:00", "2026-06-15T14:30:15"], storage_type="session"),
            ]
        )
        assert_component_equal(datetime_picker, expected)

    def test_datetimepicker_single_build(self):
        datetime_picker = vm.DateTimePicker(id="dtp", range=False, value="2026-03-01T09:00", title="Title").build()

        date_defaults = {
            "minDate": None,
            "maxDate": None,
            "valueFormat": "MMM D, YYYY",
            "persistence": True,
            "persistence_type": "session",
            "withCellSpacing": False,
            "placeholder": "Pick a date",
        }
        time_defaults = {"debounce": True, "persistence": True, "persistence_type": "session"}

        expected = html.Div(
            children=[
                dbc.Label([html.Span("Title", id="dtp_title"), None], html_for="dtp-date"),
                html.Div(
                    children=[
                        dmc.DatePickerInput(id="dtp-date", type="default", value="2026-03-01", **date_defaults),
                        dmc.TimePicker(id="dtp-time", value="09:00", **time_defaults),
                    ],
                    className="vizro_datetime_picker_single",
                ),
                dcc.Store(id="dtp", data="2026-03-01T09:00", storage_type="session"),
            ]
        )
        assert_component_equal(datetime_picker, expected)

    def test_datetimepicker_build_no_title(self):
        """When no title is set, the label is None."""
        datetime_picker = vm.DateTimePicker(id="dtp", range=False, value="2026-03-01T09:00").build()

        assert datetime_picker.children[0] is None

    def test_datetimepicker_build_date_only_value(self):
        """A date-only value (time cleared) splits into a date with an empty-string time."""
        datetime_picker = vm.DateTimePicker(id="dtp", range=False, value="2026-03-01").build()

        inner = datetime_picker.children[1].children
        assert inner[0].value == "2026-03-01"
        assert inner[1].value == ""
        assert datetime_picker.children[2].data == "2026-03-01"

    def test_datetimepicker_build_none_value(self):
        """A None value splits into (None, '') for both range ends."""
        datetime_picker = vm.DateTimePicker(id="dtp", range=True).build()

        first_pair = datetime_picker.children[1].children[0].children[1].children
        assert first_pair[0].value is None
        assert first_pair[1].value == ""
        assert datetime_picker.children[-1].data == [None, None]

    def test_datetimepicker_build_with_description(self):
        datetime_picker = vm.DateTimePicker(
            id="dtp",
            range=False,
            value="2026-03-01T09:00",
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
        label = datetime_picker.children[0]
        assert_component_equal(
            label,
            dbc.Label([html.Span("Title", id="dtp_title"), *expected_description], html_for="dtp-date"),
        )

    def test_datetimepicker_build_with_extra(self):
        """Extra keyword arguments are dispatched to whichever sub-component accepts them."""
        datetime_picker = vm.DateTimePicker(
            id="dtp",
            range=False,
            value="2026-03-01T09:00",
            # numberOfColumns is a DatePickerInput-only prop; withSeconds is a TimePicker-only prop.
            extra={"numberOfColumns": 2, "withSeconds": True},
        ).build()

        inner = datetime_picker.children[1].children
        date_input, time_input = inner[0], inner[1]
        assert date_input.numberOfColumns == 2
        assert not hasattr(time_input, "numberOfColumns") or time_input.numberOfColumns is None
        assert time_input.withSeconds is True
        assert not hasattr(date_input, "withSeconds") or date_input.withSeconds is None
