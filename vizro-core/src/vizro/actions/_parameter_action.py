"""Pre-defined action function "_parameter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture
from vizro.managers import model_manager



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
    target_ids: List[ModelID] = [target.split(".")[0] for target in targets]  # type: ignore[misc]

    figures_outputs = _get_modified_page_figures(
        targets=target_ids,
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameters=ctx.args_grouping["external"]["parameters"],
    )

    for target in targets:
        target_id, targeted_argument = target.split(".", 1)
        if targeted_argument.startswith("data_frame"):
            from vizro.models._controls import Filter
            for filter in model_manager._items_with_type(Filter):
                filter = filter[1]
                if target_id in filter.targets:
                    filter._set_categorical_selectors_options(
                        force_update=True,
                        data_load_kwargs={
                            target_id: {
                                "points": ctx.args_grouping["external"]["parameters"][0]["value"]
                            }
                        }
                    )
                    figures_outputs[filter.id] = filter.build()

    return figures_outputs
