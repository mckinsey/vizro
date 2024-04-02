"""Pre-defined action function "filter_interaction" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List, Optional

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def filter_interaction(targets: Optional[List[ModelID]] = None, **inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Filters targeted charts/components on page by clicking on data points or table cells of the source chart.

    To set up filtering on specific columns of the target graph(s), include these columns in the 'custom_data'
    parameter of the source graph e.g. `px.bar(..., custom_data=["species", "sepal_length"])`.
    If the filter interaction source is a table e.g. `vm.Table(..., actions=[filter_interaction])`,
    then the table doesn't need to have a 'custom_data' parameter set up.

    Args:
        targets: List of target component ids to filter by chart interaction. If missing, will target all valid
            components on page. Defaults to `None`.
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

    Returns:
        Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}

    """
    return _get_modified_page_figures(
        targets=targets,
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameters=ctx.args_grouping["external"]["parameters"],
    )
