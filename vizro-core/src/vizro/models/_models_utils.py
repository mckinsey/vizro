import logging
import math
from datetime import date
from functools import wraps
from typing import Union, cast

from dash import html
from pydantic import StrictBool

from vizro.models.types import CapturedCallable, OptionsType, _SupportsCapturedCallable

logger = logging.getLogger(__name__)


def _log_call(method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        # We need to run method before logging so that @_log_call works for __init__.
        return_value = method(self, *args, **kwargs)
        logger.debug("Running %s.%s for model with id %s", self.__class__.__name__, method.__name__, self.id)
        return return_value

    return _wrapper


# Validators for reuse
def check_captured_callable_model(value):
    if isinstance(value, CapturedCallable):
        captured_callable = value
    elif isinstance(value, _SupportsCapturedCallable):
        captured_callable = value._captured_callable
    else:
        return value

    raise ValueError(
        f"A callable of mode `{captured_callable._mode}` has been provided. Please wrap it inside "
        f"`{captured_callable._model_example}`."
    )


REPLACEMENT_STRINGS = {
    # "substring to match a larger general module string": "string to replace with"
    # dot required so that in the case where no replacement is used, we do not
    # have a preceding dot (see __repr_clean__ in types.py)
    "plotly.express": "px.",
    "vizro.tables": "vt.",
    "vizro.figures": "vf.",
    "vizro.actions": "va.",
    "vizro.charts": "vc.",
}


def _build_inner_layout(layout, components):
    """Builds inner layout and adds components to grid or flex. Used inside `Page`, `Container` and `Form`."""
    from vizro.models import Grid

    components_container = layout.build()
    if isinstance(layout, Grid):
        for idx, component in enumerate(components):
            components_container[f"{layout.id}_{idx}"].children = component.build()
    else:
        components_container.children = [html.Div(component.build(), className="flex-item") for component in components]

    return components_container


def validate_icon(icon) -> str:
    return icon.strip().lower().replace(" ", "_")


def _get_list_of_labels(full_options: OptionsType) -> Union[list[StrictBool], list[float], list[str], list[date]]:
    """Returns a list of labels from the selector options provided."""
    if all(isinstance(option, dict) for option in full_options):
        return [option["label"] for option in full_options]  # type: ignore[index]
    else:
        return cast(Union[list[StrictBool], list[float], list[str], list[date]], full_options)


def _calculate_option_height(full_options: OptionsType, no_characters: int = 30) -> int:
    """Calculates the height of the dropdown options based on the longest option."""
    # 30 characters is roughly the number of "A" characters you can fit comfortably on a line in the dropdown.
    # "A" is representative of a slightly wider than average character:
    # https://stackoverflow.com/questions/3949422/which-letter-of-the-english-alphabet-takes-up-most-pixels
    # We look at the longest option to find number_of_lines it requires. Option height is the same for all options
    # and needs 24px for each line + 8px padding.
    list_of_labels = _get_list_of_labels(full_options)
    max_length = max(len(str(option)) for option in list_of_labels)
    number_of_lines = math.ceil(max_length / no_characters)
    return 8 + 24 * number_of_lines
