"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Dict, List

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture
from vizro.managers import model_manager, data_manager


@capture("action")
def _on_page_load(targets: List[ModelID], **inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Applies controls to charts on page once the page is opened (or refreshed).

    Args:
        targets: List of target component ids to apply on page load mechanism to
        inputs: Dict mapping action function names with their inputs e.g.
            inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': []}

    Returns:
        Dict mapping target chart ids to modified figures e.g. {'my_scatter': Figure({})}

    """
    print("\nON PAGE LOAD - START")
    print(f'Filter value: {ctx.args_grouping["external"]["filters"]}')
    return_obj = _get_modified_page_figures(
        targets=targets,
        ctds_filter=ctx.args_grouping["external"]["filters"],
        ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        ctds_parameters=ctx.args_grouping["external"]["parameters"],
    )

    import vizro.models as vm
    from time import sleep
    sleep(1)

    # TODO-WIP: Add filters to OPL targets. Return only dynamic filter from the targets and not from the entire app.
    for filter_id, filter_obj in model_manager._items_with_type(vm.Filter):
        if filter_obj._dynamic:
            current_value = [
                item for item in ctx.args_grouping["external"]["filters"]
                if item["id"] == filter_obj.selector.id
            ][0]["value"]

            if current_value in ["ALL", ["ALL"]]:
                current_value = []

            # TODO-CONSIDER: Does calculating options/min/max significantly slow down the app?
            # TODO: Also propagate DFP values into the load() method
            # 1. "new_options"/"min/max" DOES NOT include the "current_value"
            # filter_obj._set_categorical_selectors_options(force=True, current_value=[])

            # 2. "new_options" DOES include the "current_value"
            filter_obj._set_categorical_selectors_options(force=True, current_value=current_value)
            filter_obj._set_numerical_and_temporal_selectors_values(force=True, current_value=current_value)

            return_obj[filter_id] = filter_obj.selector(on_page_load_value=current_value)

    print("ON PAGE LOAD - END\n")

    return return_obj
