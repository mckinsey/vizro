"""Pre-defined action function "_parameter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import State, ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import AbstractAction


# TODO NOW: comments and docstrings like in opl
class _parameter(AbstractAction):
    targets: list[ModelID]

    def function(
        self,
        filters,
        parameters,
        filter_interaction,
    ) -> dict[ModelID, Any]:
        # TODO NOW: work out where this goes. Probably better here than in _get_modified_page_figures.
        targets = [target.partition(".")[0] for target in self.targets]
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameter=ctx.args_grouping["external"]["parameters"],
            targets=targets,
        )

    @property
    def outputs(self):
        targets = [target.partition(".")[0] for target in self.targets]
        outputs = {}

        for target in targets:
            component_id = target
            component_property = model_manager[component_id]._output_component_property
            outputs[target] = f"{component_id}.{component_property}"

        return outputs

    # pararmeter_action
    # def _post_init(self):
    #     """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
    #     properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
    #     the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
    #     and the calculated arguments.
    #     """
    #     # TODO-AV2-OQ-*: Consider making a difference within this method between 'targets' and 'affected_arguments' e.g.
    #     #  "targets" - only target model IDs e.g. "my_scatter_chart_id"
    #     #  "affected_arguments" - affected_argument per target e.g. "layout.title.size"
    #     #  PROS:
    #     #  1. Calculate everything we can in advance so we don't have to deal with calculation every time later.
    #
    #     self._page_id = model_manager._get_model_page_id(model_id=self._action_id)
    #
    #     # Validate and calculate "targets"
    #     targets = self.targets = self._arguments.get("targets")
    #     for target in targets:
    #         if "." not in target:
    #             raise ValueError(
    #                 f"Invalid target {target}. Targets must be supplied in the from of "
    #                 "<target_component>.<target_argument>"
    #             )
    #         target_id = target.split(".")[0]
    #         if self._page_id != model_manager._get_model_page_id(model_id=target_id):
    #             raise ValueError(f"Component '{target_id}' does not exist on the page '{self._page_id}'.")
    #     self.targets = targets
