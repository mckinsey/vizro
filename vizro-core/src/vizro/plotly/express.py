"""Functionality to enable drop-in replacement that wraps plotly express figures.

Makes them compatible with the dashboard when you do `import vizro.plotly.express as px`.
Only plotly figures are wrapped; everything else is passed through unmodified, e.g. px.data.
"""

from typing import Any

import plotly.express as px

from vizro.models.types import capture


# TODO: is there a better way to see if the import is a graph? Don't want to check return type though. -> MS
# Might also want to define __dir__ or __all__ in order to facilitate IDE completion etc.
# TODO: type hints -> MS
def __getattr__(name: str) -> Any:
    px_name = getattr(px, name)
    try:
        return capture(mode="graph")(px_name) if px_name.__module__ == "plotly.express._chart_types" else px_name
    except AttributeError:
        return px_name
