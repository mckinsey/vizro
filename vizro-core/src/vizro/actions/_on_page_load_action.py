"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import State, ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import AbstractAction


# TODO NOW: rename apply_controls or similar. Docstring. Tidy comments in arguments.
class _on_page_load(AbstractAction):
    targets: list[ModelID]

    def function(
        self,
        filters,
        parameters,
        filter_interaction,
    ) -> dict[ModelID, Any]:
        # TODO NOW: comment about how filters, paramters, filter_interaction currently ignored but will be used in
        #  future when do pattern matching callback.
        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameter=ctx.args_grouping["external"]["parameters"],
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

    # update_figures
    # def _post_init(self):
    #     """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
    #     properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
    #     the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
    #     and the calculated arguments.
    #     """
    #     self._page_id = model_manager._get_model_page_id(model_id=self._action_id)
    #
    #     # Validate and calculate "targets"
    #     targets = self._arguments.get("targets")
    #     if targets:
    #         for target in targets:
    #             if self._page_id != model_manager._get_model_page_id(model_id=target):
    #                 raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
    #     else:
    #         targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
    #     self._arguments["targets"] = self.targets = targets
