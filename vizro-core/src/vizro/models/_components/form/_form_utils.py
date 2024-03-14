"""Helper functions for models inside form folder."""

from datetime import date
from typing import Union

from vizro._constants import ALL_OPTION
from vizro.models.types import MultiValueType, OptionsType, SingleValueType


def get_options_and_default(options: OptionsType, multi: bool = False):
    """Gets list of full options and default value based on user input type of `options`."""
    if multi:
        if all(isinstance(option, dict) for option in options):
            options = [{"label": ALL_OPTION, "value": ALL_OPTION}, *options]
        else:
            options = [ALL_OPTION, *options]

    if all(isinstance(option, dict) for option in options):
        # Each option is a OptionsDictType
        default_value = options[0]["value"]  # type: ignore[index]
    else:
        default_value = options[0]

    return options, default_value


# Utils for validators
def is_value_contained(value: Union[SingleValueType, MultiValueType], options: OptionsType):
    """Checks if value is contained in a list."""
    if isinstance(value, list):
        return all(item in options for item in value)
    else:
        return value in options


# Validators for reuse
def validate_options_dict(cls, values):
    """Reusable validator for the "options" argument of categorical selectors."""
    if "options" not in values or not isinstance(values["options"], list):
        return values

    for entry in values["options"]:
        if isinstance(entry, dict) and not set(entry.keys()) == {"label", "value"}:
            raise ValueError("Invalid argument `options` passed. Expected a dict with keys `label` and `value`.")
    return values


def validate_value(cls, value, values):
    """Reusable validator for the "value" argument of categorical selectors."""
    if "options" not in values or not values["options"]:
        return value

    possible_values = (
        [entry["value"] for entry in values["options"]] if isinstance(values["options"][0], dict) else values["options"]
    )

    if value and not is_value_contained(value, possible_values):
        raise ValueError("Please provide a valid value from `options`.")

    return value


def validate_max(cls, max, values):
    """Validates that the `max` is not below the `min` for a range-based input."""
    if max is None:
        return max

    if values["min"] is not None and max < values["min"]:
        raise ValueError("Maximum value of selector is required to be larger than minimum value.")
    return max


def validate_range_value(cls, value, values):
    """Validates a value or range of values to ensure they lie within specified bounds (min/max)."""
    EXPECTED_VALUE_LENGTH = 2
    if value is None:
        return value

    lvalue, hvalue = (
        (value[0], value[1])
        if isinstance(value, list) and len(value) == EXPECTED_VALUE_LENGTH
        else (value[0], value[0]) if isinstance(value, list) and len(value) == 1 else (value, value)
    )

    if (values["min"] is not None and not lvalue >= values["min"]) or (
        values["max"] is not None and not hvalue <= values["max"]
    ):
        raise ValueError("Please provide a valid value between the min and max value.")

    return value


def validate_step(cls, step, values):
    """Reusable validator for the "step" argument for sliders."""
    if step is None:
        return step

    if values["max"] is not None and step > (values["max"] - values["min"]):
        raise ValueError(
            "The step value of the slider must be less than or equal to the difference between max and min."
        )
    return step


def set_default_marks(cls, marks, values):
    if not marks and values.get("step") is None:
        marks = None
    return marks


def validate_date_picker_range(cls, range, values):
    #
    if range and values.get("value") and (isinstance(values["value"], (date, str)) or len(values["value"]) == 1):
        raise ValueError("Please set range=False if providing single date value.")

    if not range and isinstance(values.get("value"), list):
        raise ValueError("Please set range=True if providing list of date values.")

    return range
