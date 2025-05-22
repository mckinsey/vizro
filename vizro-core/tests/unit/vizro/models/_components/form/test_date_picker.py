"""Unit tests for DatePicker."""

from datetime import date, datetime

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


class TestDatePickerInstantiation:
    """Tests model instantiation."""

    def test_create_datepicker_mandatory(self):
        date_picker = vm.DatePicker()

        assert hasattr(date_picker, "id")
        assert date_picker.type == "date_picker"
        assert date_picker.min is None
        assert date_picker.max is None
        assert date_picker.value is None
        assert date_picker.title == ""
        assert date_picker.description is None
        assert date_picker.actions == []
        assert date_picker.range is True
        assert date_picker._action_outputs == {"__default__": f"{date_picker.id}.value"}
        assert date_picker._action_inputs == {"__default__": f"{date_picker.id}.value"}

    def test_create_datepicker_mandatory_and_optional(self):
        date_picker = vm.DatePicker(
            id="date-picker-id",
            min="2024-01-01",
            max="2024-12-31",
            value=["2024-03-01", "2024-04-01"],
            title="Title",
            description="Test description",
        )

        assert date_picker.id == "date-picker-id"
        assert date_picker.type == "date_picker"
        assert date_picker.min == date(2024, 1, 1)
        assert date_picker.max == date(2024, 12, 31)
        assert date_picker.value == [date(2024, 3, 1), date(2024, 4, 1)]
        assert date_picker.title == "Title"
        assert date_picker.actions == []
        assert date_picker.range is True
        assert isinstance(date_picker.description, vm.Tooltip)
        assert date_picker._action_outputs == {
            "__default__": f"{date_picker.id}.value",
            "title": f"{date_picker.id}_title.children",
            "description": f"{date_picker.description.id}-text.children",
        }
        assert date_picker._action_inputs == {"__default__": f"{date_picker.id}.value"}

    @pytest.mark.parametrize("title", ["test", """## Test header""", ""])
    def test_valid_title(self, title):
        date_picker = vm.DatePicker(title=title)

        assert date_picker.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        date_picker = vm.DatePicker(actions=[vm.Action(function=identity_action_function())])
        actions_chain = date_picker.actions[0]

        assert actions_chain.trigger.component_property == "value"

    @pytest.mark.parametrize("min, max", [("2024-01-01", None), (None, "2024-01-01"), ("2024-01-01", "2024-02-01")])
    def test_valid_min_max(self, min, max):
        date_picker = vm.DatePicker(min=min, max=max)

        assert date_picker.min == (datetime.strptime(min, "%Y-%m-%d").date() if min else None)
        assert date_picker.max == (datetime.strptime(max, "%Y-%m-%d").date() if max else None)

    def test_validate_max_invalid_min_greater_than_max(self):
        with pytest.raises(
            ValidationError, match="Maximum value of selector is required to be larger than minimum value."
        ):
            vm.DatePicker(min="2024-02-01", max="2024-01-01")

    def test_validate_max_invalid_date_format(self):
        with pytest.raises(ValidationError, match="Input should be a valid date or datetime"):
            vm.DatePicker(min="50-50-50", max="50-50-50")

    def test_validate_range_true_datepicker_value_valid(self):
        value = ["2024-01-01", "2024-02-01"]
        date_picker = vm.DatePicker(range=True, value=value)
        expected_value = [date(2024, 1, 1), date(2024, 2, 1)]
        assert date_picker.value == expected_value

    def test_validate_range_false_datepicker_value_valid(self):
        value = "2024-01-01"
        date_picker = vm.DatePicker(range=False, value=value)
        expected_value = date(2024, 1, 1)
        assert date_picker.value == expected_value

    @pytest.mark.parametrize("range, value", [(False, "2024-01-01"), (True, ["2024-01-01", "2024-02-01"])])
    def test_validate_datepicker_value_invalid(self, range, value):
        with pytest.raises(ValidationError, match="Please provide a valid value between the min and max value."):
            vm.DatePicker(min="1999-01-01", max="1999-02-01", range=range, value=value)

    @pytest.mark.parametrize("range, value", [(False, "2024-01-01"), (True, ["2024-01-01", "2024-02-01"])])
    def test_validate_datepicker_range_valid(self, range, value):
        date_picker = vm.DatePicker(min="2024-01-01", max="2024-02-01", range=range, value=value)
        assert date_picker.range == range

    @pytest.mark.parametrize(
        "range, value",
        [
            (True, "2024-01-01"),  # range True produces DateRangePicker, value needs to be list with 2 dates
            (True, ["2024-01-01"]),  # range True produces DateRangePicker, value needs to be list with 2 dates
            (False, ["2024-01-01"]),  # range False produces DatePicker, value needs to be single date
            (False, ["2024-01-01", "2024-03-01"]),  # range False produces DatePicker, value needs to be single date
        ],
    )
    def test_validate_datepicker_range_invalid(self, range, value):
        with pytest.raises(ValidationError):
            vm.DatePicker(range=range, value=value)


class TestBuildMethod:
    @pytest.mark.parametrize("range, value", [(False, "2023-01-05"), (True, ["2023-01-05", "2023-01-07"])])
    def test_datepicker_build(self, range, value):
        date_picker = vm.DatePicker(
            min="2023-01-01", max="2023-07-01", range=range, value=value, id="datepicker_id", title="Title"
        ).build()

        expected_datepicker = html.Div(
            [
                dbc.Label([html.Span("Title", id="datepicker_id_title"), None], html_for="datepicker_id"),
                dmc.DatePickerInput(
                    id="datepicker_id",
                    minDate="2023-01-01",
                    value=value,
                    maxDate="2023-07-01",
                    persistence=True,
                    persistence_type="session",
                    type="range" if range else "default",
                    allowSingleDateInRange=True,
                    withCellSpacing=False,
                ),
            ],
        )
        assert_component_equal(date_picker, expected_datepicker)

    def test_datepicker_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        date_picker = vm.DatePicker(
            id="datepicker_id",
            min="2023-01-01",
            max="2023-07-01",
            value="2023-01-05",
            range=False,
            title="Title",
            extra={"clearable": True, "placeholder": "Select a date"},
        ).build()

        expected_datepicker = html.Div(
            [
                dbc.Label([html.Span("Title", id="datepicker_id_title"), None], html_for="datepicker_id"),
                dmc.DatePickerInput(
                    id="datepicker_id",
                    minDate="2023-01-01",
                    value="2023-01-05",
                    maxDate="2023-07-01",
                    persistence=True,
                    persistence_type="session",
                    type="default",
                    allowSingleDateInRange=True,
                    withCellSpacing=False,
                    clearable=True,
                    placeholder="Select a date",
                ),
            ],
        )
        assert_component_equal(date_picker, expected_datepicker)

    def test_datepicker_build_with_description(self):
        """Test that extra arguments correctly override defaults."""
        date_picker = vm.DatePicker(
            id="datepicker_id",
            min="2023-01-01",
            max="2023-07-01",
            value="2023-01-05",
            range=False,
            title="Title",
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
        expected_datepicker = html.Div(
            [
                dbc.Label(
                    [html.Span("Title", id="datepicker_id_title"), *expected_description],
                    html_for="datepicker_id",
                ),
                dmc.DatePickerInput(
                    id="datepicker_id",
                    minDate="2023-01-01",
                    value="2023-01-05",
                    maxDate="2023-07-01",
                    persistence=True,
                    persistence_type="session",
                    type="default",
                    allowSingleDateInRange=True,
                    withCellSpacing=False,
                ),
            ],
        )
        assert_component_equal(date_picker, expected_datepicker)
