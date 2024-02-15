"""Unit tests for DatePicker."""

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

    def test_create_datepicker_mandatory(self):
        datepicker = vm.DatePicker()

        assert hasattr(datepicker, "id")
        assert datepicker.type == "date_picker"
        assert datepicker.min is None
        assert datepicker.max is None
        assert datepicker.value is None
        assert datepicker.title == ""
        assert datepicker.actions == []

    @pytest.mark.parametrize("min, max", [("2024-01-01", None), (None, "2024-01-01"), ("2024-01-01", "2024-02-01")])
    def test_valid_min_max(self, min, max):
        datepicker = vm.DatePicker(min=min, max=max)

        assert datepicker.min == (datetime.strptime(min, "%Y-%m-%d").date() if min else None)
        assert datepicker.max == (datetime.strptime(max, "%Y-%m-%d").date() if max else None)

    def test_validate_max_invalid(self):
        with pytest.raises(
            ValidationError, match="Maximum value of slider is required to be larger than minimum value."
        ):
            vm.DatePicker(min="2024-02-01", max="2024-01-01")

    @pytest.mark.parametrize("value", ["2024-01-01", "2024-02-01", "2024-01-10", date(2024, 1, 1)])
    def test_validate_datepicker_value_valid(self, value):
        datepicker = vm.DatePicker(min="2024-01-01", max="2024-02-01", value=value)

        assert datepicker.value == (datetime.strptime(value, "%Y-%m-%d").date() if isinstance(value, str) else value)

    @pytest.mark.parametrize("value", ["2023-01-01", date(2023, 1, 1)])
    def test_validate_datepicker_value_invalid(self, value):
        with pytest.raises(ValidationError, match="Please provide a valid value between the min and max value."):
            vm.DatePicker(min="2024-01-01", max="2024-02-01", value=value)

    @pytest.mark.parametrize("title", ["test", 1, 1.0, """## Test header""", ""])
    def test_valid_title(self, title):
        datepicker = vm.DatePicker(title=title)

        assert datepicker.title == str(title)

    def test_set_action_via_validator(self, identity_action_function):
        datepicker = vm.DatePicker(actions=[vm.Action(function=identity_action_function())])
        actions_chain = datepicker.actions[0]

        assert actions_chain.trigger.component_property == "value"


class TestBuildMethod:
    @pytest.mark.parametrize(
        "min, max, value",
        [("2023-01-01", "2023-02-01", "2023-01-05"), (date(2023, 1, 1), date(2023, 2, 1), date(2023, 1, 5))],
    )
    def test_datepicker_build(self, min, max, value):
        datepicker = vm.DatePicker(min=min, max=max, value=value, id="datepicker_id", title="Test title").build()
        expected_datepicker = html.Div(
            [
                html.P("Test title"),
                dmc.DatePicker(
                    id="datepicker_id",
                    minDate=min,
                    maxDate="2023-02-01",
                    value="2023-01-05",
                    persistence=True,
                    persistence_type="session",
                ),
            ],
            className="selector_container",
            id="datepicker_id_outer",
        )
        assert_component_equal(datepicker, expected_datepicker)
