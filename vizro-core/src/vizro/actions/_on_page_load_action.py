"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import State, ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import CapturedActionCallable


class _on_page_load(CapturedActionCallable):
    # RENAME apply_controls or similar
    @staticmethod
    def pure_function(
        targets: list[ModelID],  # Gets provided upfront in on_page_load(targets=...). Always there - need to populate
        # it even if empty in advance or otherwise don't know Outputs in advance.
        filters: list[State],  # Don't need to provide this until do actual on_page_load()()
        parameters: list[State],  # Don't need to provide this until do actual on_page_load()()
        filter_interaction: list[dict[str, State]],  # Don't need to provide this until do actual on_page_load()()
    ) -> dict[ModelID, Any]:
        # AM. Might we want to use self in here?
        # filters, paramters, filter_interaction currently ignored but will be used in future

        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameters=ctx.args_grouping["external"]["parameters"],
            targets=targets,
        )


# NOW THIS IS BACK TO A PURE FUNCTION, NO NEED FOR CLASS. But probably keep as class for now.
