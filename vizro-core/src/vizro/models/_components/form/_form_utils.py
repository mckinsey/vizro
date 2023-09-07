"""Helper functions for models inside form folder."""
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


# Validators for re-use
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
