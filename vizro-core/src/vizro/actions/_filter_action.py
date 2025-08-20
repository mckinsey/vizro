from typing import Any, Callable, Literal

import pandas as pd
from dash import ctx
from pydantic import Field

from vizro.actions._abstract_action import _AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.models.types import ModelID, _Controls


class _filter(_AbstractAction):
    type: Literal["_filter"] = "_filter"

    column: str = Field(description="Column to filter on.")
    filter_function: Callable[[pd.Series, Any], pd.Series] = Field(
        description="Function to apply to column to perform filtering"
    )
    targets: list[ModelID] = Field(description="Target component IDs.")

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies _controls to charts on page once filter is applied.

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.
        """
        # This is identical to _on_page_load.
        # TODO-AV2 A 1: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["_controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["_controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["_controls"]["filter_interaction"],
            targets=self.targets,
        )

    @property
    def outputs(self):  # type: ignore[override]
        return {target: target for target in self.targets}
