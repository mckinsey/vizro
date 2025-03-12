from typing import Any, Literal

from dash import ctx
from pydantic import Field

from vizro.actions import AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models.types import _Controls


class filter_interaction(AbstractAction):
    """Filters targeted charts/components on page by clicking on data points or table cells of the source chart.

    To set up filtering on specific columns of the target graph(s), include these columns in the 'custom_data'
    parameter of the source graph e.g. `px.bar(..., custom_data=["species", "sepal_length"])`.
    If the filter interaction source is a table e.g. `vm.Table(..., actions=[filter_interaction])`,
    then the table doesn't need to have a 'custom_data' parameter set up.
    """

    type: Literal["filter_interaction"] = "filter_interaction"

    # Note this has a default value, unlikely on_page_load, filter and parameter.
    targets: list[ModelID] = Field(description="Target component IDs.", default=[])

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies _controls to charts on page once the page is opened (or refreshed).

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.

        """
        # TODO: _controls is not currently used but instead taken out of the Dash context. This
        # will change in future once the structure of _controls has been worked out and we know how to pass ids through.
        # See https://github.com/mckinsey/vizro/pull/880
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["_controls"]["filters"],
            ctds_parameter=ctx.args_grouping["external"]["_controls"]["parameters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["_controls"]["filter_interaction"],
            targets=self.targets,
        )

    @property
    def outputs(self):
        outputs = {}

        for target in self.targets:
            component_id = target
            component_property = model_manager[target]._output_component_property
            outputs[target] = f"{component_id}.{component_property}"

        return outputs
