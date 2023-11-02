"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict

from dash import ctx

from vizro.actions._actions_utils import (
    _get_modified_page_figures,
)
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def _on_page_load(page_id: ModelID, **inputs: Dict[str, Any]) -> Dict[ModelID, Any]:
    """Applies controls to charts on page once the page is opened (or refreshed).

    Args:
        page_id: Page ID of relevant page
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Returns:
        Dict mapping target chart ids to modified figures e.g. {'my_scatter': Figure({})}
    """
    targets = [component.id for component in model_manager[page_id].components if data_manager._has_registered_data(component.id)]  # type: ignore[attr-defined]  # noqa: E501

    return _get_modified_page_figures(
        targets=targets,
        ctds_filter=ctx.args_grouping["filters"],
        ctds_filter_interaction=ctx.args_grouping["filter_interaction"],
        ctds_parameters=ctx.args_grouping["parameters"],
        ctd_theme=ctx.args_grouping["theme_selector"],
    )
