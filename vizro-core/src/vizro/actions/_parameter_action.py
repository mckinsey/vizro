"""Pre-defined action function "_parameter" to be re-used in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List

from dash import ctx

from vizro.actions._actions_utils import (
    _get_modified_page_charts,
)
from vizro.models.types import capture


# TODO - consider using dash.Patch() for parameter action
@capture("action")
def _parameter(targets: List[str], **inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Modifies parameters of targeted charts/components on page.

    Args:
        targets: List of target component ids to change parameters of.
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Returns:
        Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
    """
    targets = [target.split(".")[0] for target in targets]

    return _get_modified_page_charts(
        targets=targets,
        ctds_filter=ctx.args_grouping["filters"],
        ctds_filter_interaction=ctx.args_grouping["filter_interaction"],
        ctds_parameters=ctx.args_grouping["parameters"],
        ctd_theme=ctx.args_grouping["theme_selector"],
    )
