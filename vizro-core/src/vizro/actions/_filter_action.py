from typing import Any, Callable, Literal

import pandas as pd
from dash import ctx
from pydantic import Field

from vizro.actions import AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import Controls


class _filter(AbstractAction):
    type: Literal["_filter"] = "_filter"

    # TODO NOW: rename arguments to remove "filter"?
    filter_column: str = Field(description="Column to filter on.")
    filter_function: Callable[[pd.Series, Any], pd.Series] = Field(
        description="Function to apply to column to perform filtering"
    )
    targets: list[ModelID] = Field(description="Target component IDs.")

    def function(self, controls: Controls) -> dict[ModelID, Any]:
        """Applies controls to charts on page once filter is applied.

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.

        """
        # This is identical to _on_page_load.
        # TODO: controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["controls"]["filter_interaction"],
            targets=self.targets,
        )

    @property
    def outputs(self):
        # This is identical to _on_page_load.
        outputs = {}

        for target in self.targets:
            component_id = target
            component_property = model_manager[target]._output_component_property
            outputs[target] = f"{component_id}.{component_property}"

        return outputs
