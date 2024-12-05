"""Pre-defined action function "_parameter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
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
    # figure_targets: list[ModelID] = [target.split(".") for target in targets]  # type: ignore[misc]

    # need to provide current page or just get all Filters from whole dashboard
    figure_targets = targets
    filters = [
        filter for filter in cast(Iterable[Filter], model_manager._get_models(Filter, page=page)) if filter._dynamic
    ]

    filter_targets = set()

    for figure_target in figure_targets:
        figure_target_id, figure_target_argument = figure_target.split(".", 1)
        if figure_target_argument.startswith("data_frame"):
            for filter in filters:
                if figure_target_id in filter.targets:
                    filter_targets.add(filter.id)

    return _get_modified_page_figures(
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameter=ctx.args_grouping["external"]["parameters"],
        targets=figure_targets + list(filter_targets),
    )
