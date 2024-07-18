import logging
from functools import wraps

from vizro.models.types import CapturedCallable, _SupportsCapturedCallable

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
# TODO: change field to value
def validate_min_length(cls, field):
    if not field:
        raise ValueError("Ensure this value has at least 1 item.")
    return field


def check_captured_callable(cls, field):
    if not isinstance(field, (CapturedCallable, _SupportsCapturedCallable)):
        return field

    if isinstance(field, _SupportsCapturedCallable):
        field = field._captured_callable

    mode = field._mode
    model = field._model

    raise ValueError(f"A callable of mode `{mode}` has been provided. Please wrap it inside the `{model}(figure=...)`.")
