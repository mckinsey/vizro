"""Helper functions for models inside form folder."""

from datetime import date, time
from typing import Any

from pydantic import TypeAdapter, ValidationInfo

from vizro.models.types import MultiValueType, OptionsType, SingleValueType, _OptionsDictType


def get_dict_options_and_value(
    options: OptionsType, value: SingleValueType | MultiValueType | None, multi: bool
) -> tuple[list[_OptionsDictType], SingleValueType | MultiValueType]:
    """Returns `(dict_options, value)`. If input `value` is `None`, it is derived from `options`."""
    # Omitted string conversion for "label" to avoid unintended formatting issues (for example, 2002 becoming '2002.0').
    dict_options = [option if isinstance(option, dict) else {"label": option, "value": option} for option in options]

    list_values = [dict_option["value"] for dict_option in dict_options]
    default_value = list_values if multi else list_values[0]

    return dict_options, value if value is not None else default_value  # type: ignore[return-value]


# Util for vm.Slider and vm.RangeSlider
def to_int_if_whole(value: float | int) -> float | int:
    return int(value) if isinstance(value, float) and value.is_integer() else value


# Utils for validators
def is_value_contained(value: SingleValueType | MultiValueType, options: OptionsType):
    """Checks if value is contained in a list."""
    if isinstance(value, list):
        return all(item in options for item in value)
    else:
        return value in options


# Validators for reuse
def validate_options_dict(cls, data: Any) -> Any:
    """Reusable validator for the "options" argument of categorical selectors."""
    if not isinstance(data, dict) or not isinstance(data.get("options"), list):
        return data

    for option in data["options"]:
        if isinstance(option, dict):
            TypeAdapter(_OptionsDictType).validate_python(option)
    return data


def validate_value(value, info: ValidationInfo):
    """Reusable validator for the "value" argument of categorical selectors."""
    if "options" not in info.data or not info.data["options"]:
        return value

    # Unwrap each option per-element so that mixed lists produce the right set of allowed values.
    possible_values = [option["value"] if isinstance(option, dict) else option for option in info.data["options"]]

    if value is not None and not is_value_contained(value, possible_values):
        raise ValueError("Please provide a valid value from `options`.")

    return value


def validate_max(max, info: ValidationInfo):
    """Validates that the `max` is not below the `min` for a range-based input."""
    if max is None:
        return max

    if info.data["min"] is not None and max < info.data["min"]:
        raise ValueError("Maximum value of selector is required to be larger than minimum value.")
    return max


def validate_range_value(value, info: ValidationInfo):
    """Validates a value or range of values to ensure they lie within specified bounds (min/max)."""
    EXPECTED_VALUE_LENGTH = 2
    if value is None:
        return value

    lvalue, hvalue = (
        (value[0], value[1])
        if isinstance(value, list) and len(value) == EXPECTED_VALUE_LENGTH
        # TODO: I am not sure the below makes sense.
        # The field constraint on value means that it should always be a list of length 2.
        # The unit tests even check for the case where value is a list of length 1 (and it should raise an error).
        else (value[0], value[0])
        if isinstance(value, list) and len(value) == 1
        else (value, value)
    )

    if (info.data["min"] is not None and not lvalue >= info.data["min"]) or (
        info.data["max"] is not None and not hvalue <= info.data["max"]
    ):
        raise ValueError("Please provide a valid value between the min and max value.")

    return value


def validate_step(step, info: ValidationInfo):
    """Reusable validator for the "step" argument for sliders."""
    if step is None:
        return step

    if info.data["max"] is not None and step > (info.data["max"] - info.data["min"]):
        raise ValueError(
            "The step value of the slider must be less than or equal to the difference between max and min."
        )
    return step


def validate_date_time_range_picker(range, info: ValidationInfo):
    if (
        range
        and info.data.get("value")
        and (isinstance(info.data["value"], (date, time, str)) or len(info.data["value"]) == 1)
    ):
        raise ValueError("Please set range=False if providing a single value.")

    if not range and isinstance(info.data.get("value"), list):
        raise ValueError("Please set range=True if providing a list of values.")

    return range
