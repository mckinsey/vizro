import logging
from functools import wraps
from typing import List

import numpy as np
from dash import html

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


def _create_component_container(self, components_content):
    component_container = html.Div(
        components_content,
        style={
            "gridRowGap": self.layout.row_gap,
            "gridColumnGap": self.layout.col_gap,
            "gridTemplateColumns": f"repeat({len(self.layout.grid[0])}," f"minmax({self.layout.col_min_width}, 1fr))",
            "gridTemplateRows": f"repeat({len(self.layout.grid)}," f"minmax({self.layout.row_min_height}, 1fr))",
        },
        className="grid-layout",
    )
    return component_container


def _assign_component_grid_area(self):
    return [
        html.Div(
            component.build(),
            style={
                "gridColumn": f"{grid_coord.col_start}/{grid_coord.col_end}",
                "gridRow": f"{grid_coord.row_start}/{grid_coord.row_end}",
            },
        )
        for component, grid_coord in zip(self.components, self.layout.component_grid_lines)
    ]
