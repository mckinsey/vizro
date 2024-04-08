from typing import Any, Dict, List

from dash import Output, State, ctx

from vizro.managers import model_manager
from vizro.models.types import CapturedActionCallable


class ParameterAction(CapturedActionCallable):

    def _post_init(self):
        """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
        properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
        the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
        and the calculated arguments.
        """
        # TODO-AV2-OQ: Rethink validation and calculation of properties for filter/parameter/update_figures since they
        #  have been private actions. Maybe we can make them public and do validation and calculation in _post_init,
        #  here, instead inside the Filter/Parameter/Page models.

        # TODO-AV2-OQ: Consider making a difference within this method between 'targets' and 'affected_arguments' e.g.:
        #  "targets" - only target model IDs e.g. "my_scatter_chart_id"
        #  "affected_arguments" - affected_argument per target e.g. "layout.title.size"
        #  PROS:
        #  1. Calculate everything we can in advance so we don't have to deal with calculation every time later.

        self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # Validate and calculate "targets"
        self.targets = self._arguments.get("targets")

    @staticmethod
    def pure_function(targets: List[str], **inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Modifies parameters of targeted charts/components on page.

        Args:
            targets: List of target component ids to change parameters of.
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

        Returns:
            Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}

        """
        from vizro.actions._actions_utils import _get_modified_page_figures

        target_ids: List[ModelID] = [target.split(".")[0] for target in targets]  # type: ignore[misc]

        return _get_modified_page_figures(
            targets=target_ids,
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameters=ctx.args_grouping["external"]["parameters"],
        )

    @property
    def inputs(self):
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_figure_interactions,
            _get_inputs_of_filters,
            _get_inputs_of_parameters,
        )
        from vizro.actions.filter_action import FilterAction
        from vizro.actions.filter_interaction_action import FilterInteractionAction

        page = model_manager[self._page_id]
        return {
            "filters": _get_inputs_of_filters(page=page, action_class=FilterAction),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, action_class=FilterInteractionAction),
            "parameters": _get_inputs_of_parameters(page=page, action_class=ParameterAction),
            "theme_selector": State("theme_selector", "checked"),
        }

    @property
    def outputs(self) -> Dict[str, Output]:
        target_ids: List[ModelID] = [target.split(".")[0] for target in self.targets]  # type: ignore[misc]

        return {
            target: Output(
                component_id=target,
                component_property=model_manager[target]._output_component_property,
                allow_duplicate=True,
            )
            for target in target_ids
        }


# Alias for ParameterAction
parameter_action = ParameterAction
