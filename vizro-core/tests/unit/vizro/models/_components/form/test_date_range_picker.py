"""Unit tests for DateRangePicker."""

from datetime import date, datetime

import dash_mantine_components as dmc
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestDatePickerInstantiation:
    """Tests model instantiation."""

    def test_create_date_range_picker_mandatory(self):
        date_range_picker = vm.DateRangePicker()

        assert hasattr(date_range_picker, "id")
        assert date_range_picker.type == "date_range_picker"
        assert date_range_picker.min is None
        assert date_range_picker.max is None
        assert date_range_picker.value == []
        assert date_range_picker.title == ""
        assert date_range_picker.actions == []

    @pytest.mark.parametrize("min, max", [("2024-01-01", None), (None, "2024-01-01"), ("2024-01-01", "2024-02-01")])
    def test_valid_min_max(self, min, max):
        date_range_picker = vm.DateRangePicker(min=min, max=max)

        assert date_range_picker.min == (datetime.strptime(min, "%Y-%m-%d").date() if min else None)
        assert date_range_picker.max == (datetime.strptime(max, "%Y-%m-%d").date() if max else None)

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match="Maximum value of slider is required to be larger than minimum value."
        ):
            vm.DateRangePicker(min="2024-02-01", max="2024-01-01")

    @pytest.mark.parametrize(
        "value",
        [
            ["2024-01-01", "2024-01-01"],
            ["2024-02-01", "2024-02-01"],
            ["2024-01-10", "2024-01-11"],
            [date(2024, 1, 1), date(2024, 1, 2)],
            [date(2024, 1, 1), "2024-01-02"],
        ],
    )
    def test_validate_datepicker_value_valid(self, value):
        date_range_picker = vm.DateRangePicker(min="2024-01-01", max="2024-02-01", value=value)

        parsed_value = [datetime.strptime(val, "%Y-%m-%d").date() if isinstance(val, str) else val for val in value]

        assert date_range_picker.value == parsed_value

    @pytest.mark.parametrize("value", [["2023-01-01", "2025-01-01"], [date(2023, 1, 1), date(2024, 1, 1)]])
    def test_validate_date_range_picker_value_invalid(self, value):
        with pytest.raises(ValidationError, match="Please provide a valid value between the min and max value."):
            vm.DateRangePicker(min="2024-01-01", max="2024-02-01", value=value)

    @pytest.mark.parametrize("title", ["test", 1, 1.0, """## Test header""", ""])
    def test_valid_title(self, title):
        date_range_picker = vm.DateRangePicker(title=title)

        assert date_range_picker.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        date_range_picker = vm.DateRangePicker(actions=[vm.Action(function=identity_action_function())])
        actions_chain = date_range_picker.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestBuildMethod:
    @pytest.mark.parametrize(
        "min, max, value",
        [
            ("2023-01-01", "2023-02-01", ["2023-01-05", "2023-01-07"]),
            (date(2023, 1, 1), date(2023, 2, 1), [date(2023, 1, 5), date(2023, 1, 7)]),
        ],
    )
    def test_date_range_picker_build(self, min, max, value):
        date_range_picker = vm.DateRangePicker(
            min=min, max=max, value=value, id="date_range_picker_id", title="Test title"
        ).build()
        expected_date_range_picker = html.Div(
            [
                html.P("Test title"),
                dmc.DateRangePicker(
                    id="date_range_picker_id",
                    minDate=min,
                    maxDate="2023-02-01",
                    value=["2023-01-05", "2023-01-07"],
                    persistence=True,
                    persistence_type="session",
                    dropdownPosition="bottom-start",
                    clearable=False,
                ),
            ],
            className="selector_container",
            id="date_range_picker_id_outer",
        )
        assert_component_equal(date_range_picker, expected_date_range_picker)
