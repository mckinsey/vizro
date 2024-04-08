import importlib
from typing import Any, Callable, Dict, List, Literal, Optional

from dash import Output, State, ctx, dcc
from pandas import Series

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import CapturedActionCallable


class UpdateFiguresAction(CapturedActionCallable):
    def _post_init(self):
        """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
        properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
        the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
        and the calculated arguments.
        """
        self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # Validate and calculate "targets"
        targets = self._arguments.get("targets")
        if targets:
            for target in targets:
                if self._page_id != model_manager._get_model_page_id(model_id=target):
                    raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        else:
            targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        self._arguments["targets"] = self.targets = targets

    @staticmethod
    def pure_function(targets: Optional[List[ModelID]] = None, **inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Filters targeted charts/components on page by clicking on data points or table cells of the source chart.

        To set up filtering on specific columns of the target graph(s), include these columns in the 'custom_data'
        parameter of the source graph e.g. `px.bar(..., custom_data=["species", "sepal_length"])`.
        If the filter interaction source is a table e.g. `vm.Table(..., actions=[filter_interaction])`,
        then the table doesn't need to have a 'custom_data' parameter set up.

        Args:
            targets: List of target component ids to filter by chart interaction. If missing, will target all valid
                components on page. Defaults to `None`.
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
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_figure_interactions,
            _get_inputs_of_filters,
            _get_inputs_of_parameters,
        )
        from vizro.actions.filter_action import FilterAction
        from vizro.actions.filter_interaction_action import FilterInteractionAction
        from vizro.actions.parameter_action import ParameterAction

        page = model_manager[self._page_id]

        return {
            "filters": _get_inputs_of_filters(page=page, action_class=FilterAction),
            "filter_interaction": _get_inputs_of_figure_interactions(
                page=page, action_class=FilterInteractionAction
            ),
            "parameters": _get_inputs_of_parameters(page=page, action_class=ParameterAction),
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


# Alias for UpdateFiguresAction
update_figures = UpdateFiguresAction
