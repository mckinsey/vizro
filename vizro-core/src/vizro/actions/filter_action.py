from typing import Any, Callable, Dict, List

from dash import Output, State, ctx
from pandas import Series

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import CapturedActionCallable


class FilterAction(CapturedActionCallable):
    def _post_init(self):
        """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
        properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
        the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
        and the calculated arguments.
        """
        # TODO-AV2-OQ: Rethink validation and calculation of properties for filter/parameter/update_figures since they
        #  have been private actions before.

        self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # TODO-AV2: Should we rename it to `column`?
        # Validate and calculate "filter_column"
        filter_column = self._arguments.get("filter_column")
        if not filter_column or not isinstance(filter_column, str):
            raise ValueError("'filter_column' must be a string.")

        # TODO-AV2: Should we: 
        #  1. Rename it to `filtering_function`?
        #  2. Calculate it based on the 'filter_column' type (something similar we do in the Filter._pre_build() phase)?
        # Validate and calculate "filter_function"
        filter_function = self._arguments.get("filter_function")
        if not filter_function or not callable(filter_function):
            raise ValueError("'filter_function' must be a callable.")

        # Validate and calculate "targets"
        targets = self._arguments.get("targets")
        if targets:
            for target in targets:
                if self._page_id != model_manager._get_model_page_id(model_id=target):
                    raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        else:
            targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        # targets are assigned to self.targets because self.targets is used in outputs calculation.
        # targets are assigned to self._arguments["targets"] because targets could be calculated in this method so we
        # should ensure that the calculated targets are used in pure_function.
        self._arguments["targets"] = self.targets = targets

    @staticmethod
    def pure_function(
        filter_column: str,
        targets: List[ModelID],
        filter_function: Callable[[Series, Any], Series],
        **inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Filters targeted charts/components on page by interaction with `Filter` control.

        Args:
            filter_column: Data column to filter
            targets: List of target component ids to apply filters on
            filter_function: Filter function to apply
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': [], 'theme_selector': True}

        Returns:
            Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}

        """
        from vizro.actions._actions_utils import _get_modified_page_figures

        return _get_modified_page_figures(
            targets=targets,
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameters=ctx.args_grouping["external"]["parameters"],
        )

    @property
    def inputs(self):
        from vizro.actions import filter_interaction, parameter_action
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_figure_interactions,
            _get_inputs_of_filters,
            _get_inputs_of_parameters,
        )

        # TODO-AV2-OQ: Consider the following inputs ctx form:
        #  ```
        #  return {
        #      target_1: {'filters': ..., 'parameters': ..., 'filter_interaction': ..., 'theme_selector': ...},
        #      target_2: {'filters': ..., 'parameters': ..., 'filter_interaction': ..., 'theme_selector': ...},
        #  }
        #  ```
        #  Pros:
        #  1. We don't need anymore to send all filter/parameters/filter_interaction inputs to the server
        #  2. Potentially we don't need to dig through the ctx in the _actions_utils.py which decreases the complexity

        page = model_manager[self._page_id]
        return {
            "filters": _get_inputs_of_filters(page=page, action_class=filter_action),
            "filter_interaction": _get_inputs_of_figure_interactions(page=page, action_class=filter_interaction),
            "parameters": _get_inputs_of_parameters(page=page, action_class=parameter_action),
            # TODO-AV2-OQ: Propagate theme_selector only if it exists on the page (could be overwritten by the user)
            "theme_selector": State("theme_selector", "checked"),
        }

    @property
    def outputs(self) -> Dict[str, Output]:
        return {
            target: Output(
                component_id=target,
                component_property=model_manager[target]._output_component_property,
                allow_duplicate=True,
            )
            for target in self.targets
        }


# Alias for FilterAction
filter_action = FilterAction
