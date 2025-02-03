"""Helper functions for models inside form folder."""

from datetime import date
from typing import Any, Optional, Union

from pydantic import ValidationInfo

from vizro._constants import ALL_OPTION
from vizro.models.types import MultiValueType, OptionsType, SingleValueType


def get_options_and_default(options: OptionsType, multi: bool = False) -> tuple[OptionsType, SingleValueType]:
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
def validate_options_dict(cls, data: Any) -> Any:
    """Reusable validator for the "options" argument of categorical selectors."""
    if "options" not in data or not isinstance(data["options"], list):
        return data

    for entry in data["options"]:
        if isinstance(entry, dict) and not set(entry.keys()) == {"label", "value"}:
            raise ValueError("Invalid argument `options` passed. Expected a dict with keys `label` and `value`.")
    return data


def validate_value(value, info: ValidationInfo):
    """Reusable validator for the "value" argument of categorical selectors."""
    if "options" not in info.data or not info.data["options"]:
        return value

    possible_values = (
        [entry["value"] for entry in info.data["options"]]
        if isinstance(info.data["options"][0], dict)
        else info.data["options"]
    )

    if hasattr(value, "__iter__") and ALL_OPTION in value:
        return value

    if value and not is_value_contained(value, possible_values):
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


def set_default_marks(
    marks: Optional[dict[float, str]], info: ValidationInfo
) -> Optional[dict[Union[float, int], str]]:
    if not marks and info.data.get("step") is None:
        marks = None

    # Dash has a bug where marks provided as floats that can be converted to integers are not displayed.
    # So we need to convert the floats to integers if possible.
    # https://github.com/plotly/dash-core-components/issues/159#issuecomment-380581043
    if marks:
        marks = {int(k) if k.is_integer() else k: v for k, v in marks.items()}
    return marks


def validate_date_picker_range(range, info: ValidationInfo):
    if (
        range
        and info.data.get("value")
        and (isinstance(info.data["value"], (date, str)) or len(info.data["value"]) == 1)
    ):
        raise ValueError("Please set range=False if providing single date value.")

    if not range and isinstance(info.data.get("value"), list):
        raise ValueError("Please set range=True if providing list of date values.")

    return range
