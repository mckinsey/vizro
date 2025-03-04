"""Pre-defined action function "_filter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Callable

from dash import State, ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID, model_manager
from vizro.models._action._action import AbstractAction

"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""


# TODO NOW: comments and docstrings like in opl


class _filter(AbstractAction):
    targets: list[ModelID]
    filter_column: str
    filter_function: Callable

    def function(
        self,
        filters,
        parameters,
        filter_interaction,
    ) -> dict[ModelID, Any]:
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


# TODO NOW: validation
# filter_action
# def _post_init(self):
#     """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
#     properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
#     the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
#     and the calculated arguments.
#     """
#     # TODO-AV2-OQ: Rethink validation and calculation of properties for filter/parameter/update_figures since they
#     #  have been private actions before.
#
#     self._page_id = model_manager._get_model_page_id(model_id=self._action_id)
#
#     # TODO-AV2: Should we rename it to `column`?
#     # Validate and calculate "filter_column"
#     filter_column = self._arguments.get("filter_column")
#     if not filter_column or not isinstance(filter_column, str):
#         raise ValueError("'filter_column' must be a string.")
#
#     # TODO-AV2: Should we:
#     #  1. Rename it to `filtering_function`?
#     #  2. Calculate it based on the 'filter_column' type (something similar we do in the Filter._pre_build() phase)?
#     # Validate and calculate "filter_function"
#     filter_function = self._arguments.get("filter_function")
#     if not filter_function or not callable(filter_function):
#         raise ValueError("'filter_function' must be a callable.")
#
#     # Validate and calculate "targets"
#     targets = self._arguments.get("targets")
#     if targets:
#         for target in targets:
#             if self._page_id != model_manager._get_model_page_id(model_id=target):
#                 raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
#     else:
#         targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
#     # targets are assigned to self.targets because self.targets is used in outputs calculation.
#     # targets are assigned to self._arguments["targets"] because targets could be calculated in this method so we
#     # should ensure that the calculated targets are used in pure_function.
#     self._arguments["targets"] = self.targets = targets
