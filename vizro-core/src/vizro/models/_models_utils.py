import logging
from functools import wraps
from typing import TYPE_CHECKING, List

import numpy as np

from vizro._constants import EMPTY_SPACE_CONST

if TYPE_CHECKING:
    pass

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


# Validators for reuse
def set_components(cls, components):
    if not components:
        raise ValueError("Ensure this value has at least 1 item.")
    return components


def set_layout(cls, layout, values):
    from vizro.models import Layout

    if "components" not in values:
        return layout

    if layout is None:
        grid = [[i] for i in range(len(values["components"]))]
        return Layout(grid=grid)

    unique_grid_idx = get_unique_grid_component_ids(layout.grid)
    if len(unique_grid_idx) != len(values["components"]):
        raise ValueError("Number of page and grid components need to be the same.")
    return layout
