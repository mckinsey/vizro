import logging
from functools import wraps

from dash import html

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
def set_components(cls, components):
    if not components:
        raise ValueError("Ensure this value has at least 1 item.")
    return components


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
