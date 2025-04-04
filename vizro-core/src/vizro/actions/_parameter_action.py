"""Pre-defined action function "_parameter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


@capture("action")
def _parameter(targets: list[str], **inputs: dict[str, Any]) -> dict[ModelID, Any]:
    """Modifies parameters of targeted charts/components on page.

    Args:
        targets: List of target component ids to change parameters of.
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': []}

    Returns:
        Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}

    """
    # Targets without "." are implicitly added by the `Parameter._set_actions` method
    # to handle cases where a dynamic data parameter affects a filter or its targets.
    target_ids: list[ModelID] = [target.split(".")[0] if "." in target else target for target in targets]  # type: ignore[misc]

    return _get_modified_page_figures(
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameter=ctx.args_grouping["external"]["parameters"],
        targets=target_ids,
    )
