"""Pre-defined action function "_on_page_load" to be reused in `action` parameter of VizroBaseModels."""

from typing import Any

from dash import ctx

from vizro.actions._actions_utils import _get_modified_page_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture

from typing import Any, Callable, Dict, List

from dash import Output, State, ctx
from pandas import Series

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models.types import CapturedActionCallable


class _on_page_load(CapturedActionCallable):
    @staticmethod
    def pure_function(targets: list[ModelID], **inputs: dict[str, Any]) -> dict[ModelID, Any]:
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

        page_id = model_manager._get_model_page_id(model_id=self._action_id)
        page = model_manager[page_id]
        # use List[State]
        action_input_mapping = {
            "filters": _get_inputs_of_controls(page=page, control_type=Filter),
            "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
            # TODO: Probably need to adjust other inputs to follow the same structure list[dict[str, State]]
            "filter_interaction": _get_inputs_of_figure_interactions(
                page=page, action_function=filter_interaction.__wrapped__
            ),
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
