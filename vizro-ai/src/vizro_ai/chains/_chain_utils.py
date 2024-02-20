"""Chain Utils."""

import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def _log_time(func):
    """Decorator to measure the execution time."""

    @wraps(func)
    def _wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__module__}.{func.__name__} took {end_time - start_time:.4f} seconds to run.")
        return result

    return _wrapper
