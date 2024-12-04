"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

import abc
from typing import Any, TypedDict

from dash import Output, State, ctx
from dash.development.base_component import Component

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.actions._callback_mapping._callback_mapping_utils import (
    _get_inputs_of_controls,
    _get_inputs_of_figure_interactions,
)
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Filter, Parameter
from vizro.models.types import CapturedCallable


"""
selector.actions = [FilterAction(column="blah")] # like partial action
selector.actions = [OPLAction(filter={column="blah"})]
"""


class ControlInputs(TypedDict):
    filters: list[State]
    parameters: list[State]
    filter_interaction: list[dict[str, State]]


# TODO NOW: figure out where this class lives


class CapturedActionCallable(CapturedCallable, abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(self.function, *args, **kwargs)
        self._action = None
        self._mode = "action"

    @staticmethod
    @abc.abstractmethod
    def function():
        pass

    @property
    def outputs(self) -> dict[ModelID, Output]:
        # TODO NOW: tidy and decide where this bit of code goes and how to get targets for filter and opl vs. parameter

        targets = list(self["targets"])
        output_targets = []
        for target in targets:
            if "." in target:
                component, property = target.split(".", 1)
                output_targets.append(component)
            else:
                output_targets.append(target)

        return {
            target: Output(
                component_id=target,
                component_property=model_manager[target]._output_component_property,
                allow_duplicate=True,
            )
            for target in output_targets
        }

    @property
    def inputs(self) -> ControlInputs:
        page = model_manager._get_model_page(self._action)

        # TODO NOW: create comment about refactoring ctds format in future. Comment that List[State] here would match
        #  custom actions.
        # TODO NOW: tidy comment.
        # For now just always provide arguments; in future might want to do
        # inspect.signature(self.function.pure_function).parameters to see if they're actually requested.
        # Like how pydantic handles arguments for field_validator.
        # If @capture("action") for user action produces CapturedActionCallable then must check if argument is demanded.
        # Could have logic here that looks at arguments in signature of pure_function to see what inputs should be

        return {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page),
        }

    @property
    def components(self) -> list[Component]:
        return []


# TODO NOW: rename apply_controls or similar. Docstring. Tidy comments in arguments.
class _on_page_load(CapturedActionCallable):
    @staticmethod
    def function(
        targets: list[
            ModelID
        ],  # Gets provided upfront in on_page_load(targets=...). Always there - need to populate it even if empty in advance or otherwise don't know Outputs in advance.
        filters: list[State],  # Don't need to provide this until do actual on_page_load()()
        parameters: list[State],  # Don't need to provide this until do actual on_page_load()()
        filter_interaction: list[dict[str, State]],  # Don't need to provide this until do actual on_page_load()()
    ) -> dict[ModelID, Any]:
        """Applies controls to charts on page once the page is opened (or refreshed).

        Args:
            targets: List of target component ids to filter by chart interaction. If missing, will target all valid
                components on page. Defaults to `None`.
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

        Returns:
            Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
        """
        # TODO NOW: comment about how filters, paramters, filter_interaction currently ignored but will be used in
        #  future when do pattern matching callback.

        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameter=ctx.args_grouping["external"]["parameters"],
            targets=targets,
        )

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

    # filter_interaction_action
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
    #
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
