"""Unit tests for DatePicker."""

from datetime import date, datetime

import dash_mantine_components as dmc
import pytest
from asserts import assert_component_equal
from dash import dcc, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
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
        assert date_picker.actions == []
        assert date_picker.range is True

    @pytest.mark.parametrize("min, max", [("2024-01-01", None), (None, "2024-01-01"), ("2024-01-01", "2024-02-01")])
    def test_valid_min_max(self, min, max):
        date_picker = vm.DatePicker(min=min, max=max)

        assert date_picker.min == (datetime.strptime(min, "%Y-%m-%d").date() if min else None)
        assert date_picker.max == (datetime.strptime(max, "%Y-%m-%d").date() if max else None)

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match="Maximum value of slider is required to be larger than minimum value."
        ):
            vm.DatePicker(min="2024-02-01", max="2024-01-01")

    @pytest.mark.parametrize("value", ["2024-01-01", date(2024, 1, 1), ["2024-01-01", "2024-02-01"]])
    def test_validate_datepicker_value_valid(self, value):
        date_picker = vm.DatePicker(min="2024-01-01", max="2024-02-01", value=value)
        value_to_date = (
            [datetime.strptime(value[0], "%Y-%m-%d").date(), datetime.strptime(value[1], "%Y-%m-%d").date()]
            if isinstance(value, list)
            else datetime.strptime(value, "%Y-%m-%d").date() if isinstance(value, str) else value
        )

        assert date_picker.value == value_to_date

    @pytest.mark.parametrize("value", ["2023-01-01", date(2023, 1, 1)])
    def test_validate_datepicker_value_invalid(self, value):
        with pytest.raises(ValidationError, match="Please provide a valid value between the min and max value."):
            vm.DatePicker(min="2024-01-01", max="2024-02-01", value=value)

    @pytest.mark.parametrize("title", ["test", 1, 1.0, """## Test header""", ""])
    def test_valid_title(self, title):
        date_picker = vm.DatePicker(title=title)

        assert date_picker.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        date_picker = vm.DatePicker(actions=[vm.Action(function=identity_action_function())])
        actions_chain = date_picker.actions[0]

        assert actions_chain.trigger.component_property == "value"

    @pytest.mark.parametrize("range, value", [(True, ["2024-01-01", "2024-03-01"]), (False, "2024-01-01")])
    def test_validate_datepicker_range_valid(self, range, value):
        date_picker = vm.DatePicker(min="2024-01-01", max="2024-04-01", value=value, range=range)
        value_to_date = (
            [datetime.strptime(value[0], "%Y-%m-%d").date(), datetime.strptime(value[1], "%Y-%m-%d").date()]
            if isinstance(value, list)
            else datetime.strptime(value, "%Y-%m-%d").date()
        )
        assert date_picker.value == value_to_date

    @pytest.mark.parametrize(
        "range, value",
        [
            (True, "2024-01-01"),  # range True produces DateRangePicker, value needs to be list with 2 dates
            (False, ["2024-01-01", "2024-03-01"]),  # range False produces DatePicker, value needs to single date
        ],
    )
    def test_validate_datepicker_range_invalid(self, range, value):
        with pytest.raises(ValidationError):
            vm.DatePicker(min="2024-01-01", max="2024-04-01", value=value, range=range)


class TestBuildMethod:
    @pytest.mark.parametrize(
        "value, range",
        [
            ("2023-01-05", False),
            (date(2023, 1, 5), False),
            (["2023-01-05", "2023-01-07"], True),
            ([date(2023, 1, 5), date(2023, 1, 7)], True),
        ],
    )
    def test_datepicker_build(self, value, range):
        date_picker = vm.DatePicker(
            min="2023-01-01", max="2023-07-01", value=value, id="datepicker_id", title="Test title", range=range
        ).build()

        date_picker_class = dmc.DateRangePicker if range else dmc.DatePicker
        additional_kwargs = {"allowSingleDateInRange": True} if range else {}
        expected_datepicker = html.Div(
            [
                html.Label("Test title", htmlFor="datepicker_id"),
                date_picker_class(
                    id="datepicker_id",
                    minDate="2023-01-01",
                    maxDate="2023-07-02",
                    value=value,
                    persistence=True,
                    persistence_type="session",
                    dropdownPosition="bottom-start",
                    disabledDates="2023-07-02",
                    clearable=False,
                    **additional_kwargs,
                ),
                dcc.Store(id="datepicker_id_input_store", storage_type="session", data=value),
            ],
            className="selector_container",
            id="datepicker_id_outer",
        )
        assert_component_equal(date_picker, expected_datepicker)
