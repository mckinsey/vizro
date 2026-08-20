"""Functionality to enable drop-in replacement that wraps plotly express figures.

Makes them compatible with the dashboard when you do `import vizro.plotly.express as px`.
Only plotly figures are wrapped; everything else is passed through unmodified, e.g. px.data.
"""

from typing import Any

import plotly.express as px

from vizro.models.types import capture

_PLOTLY_EXPRESS_CHART_MODULE = "plotly.express._chart_types"


def _is_plotly_express_chart_function(function: Any) -> bool:
    """Whether `function` is one of the real plotly.express chart functions (e.g. px.bar, px.scatter)."""
    return getattr(function, "__module__", None) == _PLOTLY_EXPRESS_CHART_MODULE


# TODO: is there a better way to see if the import is a graph? Don't want to check return type though. -> MS
# Might also want to define __dir__ or __all__ in order to facilitate IDE completion etc.
# TODO: type hints -> MS
def __getattr__(name: str) -> Any:
    px_name = getattr(px, name)
    return capture(mode="graph")(px_name) if _is_plotly_express_chart_function(px_name) else px_name
