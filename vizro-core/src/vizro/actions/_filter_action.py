"""Pre-defined action function "_filter" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any, Callable

import pandas as pd
from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture


# @capture("action")
# def _filter(
#     filter_column: str,
#     targets: list[ModelID],
#     filter_function: Callable[[pd.Series, Any], pd.Series],
#     **inputs: dict[str, Any],
# ) -> dict[ModelID, Any]:
#     """Filters targeted charts/components on page by interaction with `Filter` control.
#
#     Args:
#         filter_column: Data column to filter
#         targets: List of target component ids to apply filters on
#         filter_function: Filter function to apply
#         inputs: Dict mapping action function names with their inputs e.g.
#             inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': []}
#
#     Returns:
#         Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
#     """
#     return _get_modified_page_figures(
#         ctds_filter=ctx.args_grouping["external"]["filters"],
#         ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
#         ctds_parameters=ctx.args_grouping["external"]["parameters"],
#         targets=targets,
#     )


from typing import Any, Callable, Dict, List

from dash import Output, State, ctx
from pandas import Series

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import CapturedActionCallable


class _filter(CapturedActionCallable):
    def _post_init(self):
        """Post initialization is called in the vm.Action build phase, and it is used to validate and calculate the
        properties of the CapturedActionCallable. With this, we can validate the properties and raise errors before
        the action is built. Also, "input"/"output"/"components" properties and "pure_function" can use these validated
        and the calculated arguments.
        """
        # TODO-AV2-OQ: Rethink validation and calculation of properties for filter/parameter/update_figures since they
        #  have been private actions before.

        # self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # TODO-AV2: Should we rename it to `column`?
        # Validate and calculate "filter_column"
        # filter_column = self["filter_column"]
        # if not filter_column or not isinstance(filter_column, str):
        #     raise ValueError("'filter_column' must be a string.")

        # TODO-AV2: Should we:
        #  1. Rename it to `filtering_function`?
        #  2. Calculate it based on the 'filter_column' type (something similar we do in the Filter._pre_build() phase)?
        # Validate and calculate "filter_function"
        # filter_function = self._arguments.get("filter_function")
        # if not filter_function or not callable(filter_function):
        #     raise ValueError("'filter_function' must be a callable.")

        # Validate and calculate "targets"
        # targets = self._arguments.get("targets")
        # if targets:
        #     for target in targets:
        #         if self._page_id != model_manager._get_model_page_id(model_id=target):
        #             raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        # else:
        #     targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        # targets are assigned to self.targets because self.targets is used in outputs calculation.
        # targets are assigned to self._arguments["targets"] because targets could be calculated in this method so we
        # should ensure that the calculated targets are used in pure_function.
        # AM. why need this? It's already done in Filter model itself?
        # self._arguments["targets"] = targets
        pass

    @staticmethod
    def pure_function(
            filter_column: str,
            targets: list[ModelID],
            filter_function: Callable[[pd.Series, Any], pd.Series],
            **inputs: dict[str, Any],
    ) -> dict[ModelID, Any]:
        """Filters targeted charts/components on page by interaction with `Filter` control.

        Args:
            filter_column: Data column to filter
            targets: List of target component ids to apply filters on
            filter_function: Filter function to apply
            inputs: Dict mapping action function names with their inputs e.g.
                inputs = {'filters': [], 'parameters': ['gdpPercap'], 'filter_interaction': []}

        Returns:
            Dict mapping target component ids to modified charts/components e.g. {'my_scatter': Figure({})}
        """
        # AM. Might we want to use self in here?

        return _get_modified_page_figures(
            ctds_filter=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
            ctds_parameters=ctx.args_grouping["external"]["parameters"],
            targets=targets,
        )

    @property
    def inputs(self):
        from vizro.actions._callback_mapping._callback_mapping_utils import (
            _get_inputs_of_figure_interactions,
        )
        from vizro.actions._callback_mapping._callback_mapping_utils import _get_inputs_of_controls
        from vizro.actions import filter_interaction
        from vizro.models import Filter, Parameter

        # AM. think of better way to do this. OK for now though. In future maybe pattern matching callback best to
        # avoid all these lookups? May have problem with this and changes to pass id through into callbacks using
        # dict[str, State] - doesn't seem possible with pattern matching callbacks?
        page_id = model_manager._get_model_page_id(model_id=self._action_id)
        page = model_manager[page_id]
        action_input_mapping = {
            "filters": _get_inputs_of_controls(
                page=page, control_type=Filter
            ),  # AM now looks like "filters": {"filter_id": ["iris", "versicolor"]}
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),  # AM: updated
            # TODO: Probably need to adjust other inputs to follow the same structure list[dict[str, State]]
            "filter_interaction": _get_inputs_of_figure_interactions(
                page=page, action_function=filter_interaction.__wrapped__
            ),  # AM: not updated yet
        }
        return action_input_mapping

    @property
    def outputs(self) -> dict[ModelID, Output]:
        return {
            target: Output(
                component_id=target,
                component_property=model_manager[target]._output_component_property,
                allow_duplicate=True,
            )
            for target in self["targets"]
        }
