import warnings
from functools import wraps


def _state_modifier(method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        if self._frozen_state:
            warnings.warn(
                f"{method.__qualname__} modifies global state. Doing this after the dashboard has been built will "
                f"not work reliably if you run the dashboard with multiple processes.",
                RuntimeWarning,
                stacklevel=2,
            )
        return method(self, *args, **kwargs)

    return _wrapper
