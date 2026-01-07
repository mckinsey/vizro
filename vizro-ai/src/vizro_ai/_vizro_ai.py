import logging
from typing import deprecated

import pandas as pd

logger = logging.getLogger(__name__)


@deprecated("VizroAI is deprecated and will be removed in a future version. Use the chart_agent instead.")
class VizroAI:
    """Vizro-AI main class."""

    def __init__(self, model: str | None = None):
        """Initialization of VizroAI."""
        raise RuntimeError(
            "VizroAI is deprecated and will be removed in a future version. Use the chart_agent instead."
        )

    def plot(
        self,
        df: pd.DataFrame,
        user_input: str,
        max_debug_retry: int = 1,
        return_elements: bool = False,
        validate_code: bool = True,
        _minimal_output: bool = False,
    ):
        """Plot visuals using vizro via english descriptions, english to chart translation."""
        raise RuntimeError("""VizroAI.plot is deprecated since version 0.4.0. Please use the chart_agent instead.""")

    def dashboard(
        self,
        dfs: list[pd.DataFrame],
        user_input: str,
        return_elements: bool = False,
    ):
        """Creates a Vizro dashboard using english descriptions."""
        raise RuntimeError("""VizroAI.dashboard is deprecated since version 0.4.0. There is no replacement for this function.
If you are interested in genAI assisted dashboard generation, please let us know by creating an issue on GitHub or
use the Vizro MCP server instead.""")
