import logging
from functools import wraps
from typing import List

import numpy as np

from vizro._constants import EMPTY_SPACE_CONST

logger = logging.getLogger(__name__)


def _log_call(method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        # We need to run method before logging so that @_log_call works for __init__.
        return_value = method(self, *args, **kwargs)
        logger.debug("Running %s.%s for model with id %s", self.__class__.__name__, method.__name__, self.id)
        return return_value

    return _wrapper


def get_unique_grid_component_ids(grid: List[List[int]]):
    unique_grid_idx = np.unique(grid)
    unique_grid_comp_idx = unique_grid_idx[unique_grid_idx != EMPTY_SPACE_CONST]
    return unique_grid_comp_idx
