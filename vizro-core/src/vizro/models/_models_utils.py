import logging
from functools import wraps

from vizro.models.types import CapturedCallable, _DashboardReadyFigure

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
def validate_min_length(cls, field):
    if not field:
        raise ValueError("Ensure this value has at least 1 item.")
    return field


def check_captured_callable(cls, field):
    mode_to_error = {
        "figure": "A callable of mode `figure` has been provided. Please wrap it inside the `vm.Figure(figure=...)`.",
        "table": "A callable of mode `table` has been provided. Please wrap it inside the `vm.Table(figure=...)`.",
        "ag_grid": "A callable of mode `ag_grid` has been provided. Please wrap it inside the `vm.AgGrid(figure=...)`.",
        "graph": "A callable of mode `graph` has been provided. Please wrap it inside the `vm.Graph(figure=...)`.",
    }

    for component in field:
        if isinstance(component, (_DashboardReadyFigure, CapturedCallable)):
            mode = (
                component._captured_callable._mode if isinstance(component, _DashboardReadyFigure) else component._mode
            )
            error_message = mode_to_error.get(mode)
            if error_message:
                raise ValueError(error_message)

    return field
