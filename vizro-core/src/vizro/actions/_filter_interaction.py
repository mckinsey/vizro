from collections.abc import Iterable
from typing import Any, Literal, cast

from dash import ctx
from pydantic import Field

from vizro.actions import AbstractAction
from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import model_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._models_utils import _log_call
from vizro.models.types import FigureType, FigureWithFilterInteractionType, ModelID, _Controls


class filter_interaction(AbstractAction):
    """Filters targeted charts/components on page by clicking on data points or table cells of the source chart.

    To set up filtering on specific columns of the target graph(s), include these columns in the 'custom_data'
    parameter of the source graph e.g. `px.bar(..., custom_data=["species", "sepal_length"])`.
    If the filter interaction source is a table e.g. `vm.Table(..., actions=[filter_interaction])`,
    then the table doesn't need to have a 'custom_data' parameter set up.

    Args:
        targets (list[ModelID]): Target component to be affected by filter. If none are given then target all
            valid components on the page.
    """

    type: Literal["filter_interaction"] = "filter_interaction"

    # Note this has a default value, unlike on_page_load, filter and parameter.
    targets: list[ModelID] = Field(description="Target component IDs.", default=[])

    def _get_triggered_model(self) -> FigureWithFilterInteractionType:  # type: ignore[return]
        """Gets the model that triggers the action with "action_id"."""
        # In future we should have a better way of doing this:
        #  - maybe through the model manager
        #  - pass trigger into callback as a built-in keyword
        #  - maybe need to be able to define inputs property for actions that subclass AbstractAction
        for actions_chain in cast(Iterable[ActionsChain], model_manager._get_models(ActionsChain)):
            if self in actions_chain.actions:
                return model_manager[actions_chain.trigger.component_id]

    @_log_call
    def pre_build(self):
        # Check that the triggered model has the required attributes (e.g. Graph does but Button doesn't).
        # This could potentially be done with isinstance and FigureWithFilterInteractionType but filter_interaction
        # will be removed in future anyway.
        triggered_model = self._get_triggered_model()
        required_attributes = ["_filter_interaction_input", "_filter_interaction"]
        for attribute in required_attributes:
            if not hasattr(triggered_model, attribute):
                raise ValueError(f"Model {triggered_model.id} does not have required attribute `{attribute}`.")
            if "modelID" not in triggered_model._filter_interaction_input:
                raise ValueError(
                    f"Model {triggered_model.id} does not have required State `modelID` in `_filter_interaction_input`."
                )

    def function(self, _controls: _Controls) -> dict[ModelID, Any]:
        """Applies _controls to charts on page once the page is opened (or refreshed).

        Returns:
            Dict mapping target chart ids to modified figures e.g. {"my_scatter": Figure(...)}.
        """
        # TODO NEXT A 1: _controls is not currently used but instead taken out of the Dash context. This
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
            component_property = cast(FigureType, model_manager[target])._output_component_property
            outputs[target] = f"{component_id}.{component_property}"

        return outputs
