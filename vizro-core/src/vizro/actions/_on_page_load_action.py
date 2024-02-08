"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def _on_page_load(targets: List[ModelID], **inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Applies controls to charts on page once the page is opened (or refreshed).

    Args:
        targets: List of target component ids to apply on page load mechanism to
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Returns:
        Dict mapping target chart ids to modified figures e.g. {'my_scatter': Figure({})}

    """
    return _get_modified_page_figures(
        targets=targets,
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameters=ctx.args_grouping["external"]["parameters"],
    )
