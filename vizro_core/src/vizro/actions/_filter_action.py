"""Pre-defined action function "_filter" to be re-used in `action` parameter of VizroBaseModels."""

from typing import Any, Callable, Dict, List

import pandas as pd
from dash import ctx

from vizro.actions._actions_utils import (
    _get_modified_page_charts,
)
from vizro.models.types import capture


@capture("action")
def _filter(
    filter_column: str,
    targets: List[str],
    filter_function: Callable[[pd.Series, Any], pd.Series],
    **inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Filters targeted charts/components on page by interaction with `Filter` control.

    Args:
        filter_column: Data column to filter
        targets: List of target component ids to apply filters on
        filter_function: Filter function to apply
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Returns:
        Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
    """
    return _get_modified_page_charts(
        targets=targets,
        ctds_filter=ctx.args_grouping["filters"],
        ctds_filter_interaction=ctx.args_grouping["filter_interaction"],
        ctds_parameters=ctx.args_grouping["parameters"],
        ctd_theme=ctx.args_grouping["theme_selector"],
    )
