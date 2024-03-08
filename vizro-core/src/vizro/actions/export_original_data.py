from __future__ import annotations

from vizro.models.types import CapturedActionCallable
from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, List, Optional
from dash import ctx, dcc, Output, State

from vizro.actions import filter_interaction
from vizro.actions._filter_action import _filter
from vizro.managers import data_manager, model_manager

if TYPE_CHECKING:
    from vizro.models import Page
    from vizro.models._table import Table

import importlib
from vizro.managers._model_manager import ModelID
import vizro.models as vm

from vizro.actions._actions_utils import _get_filtered_data


def _get_matching_actions_by_function(
    page_id: ModelID, action_function: Callable[[Any], Dict[str, Any]]
) -> List[Action]:
    """Gets list of `Actions` on triggered `Page` that match the provided `action_function`."""
    return [
        action
        for actions_chain in model_manager._get_page_actions_chains(page_id=page_id)
        for action in actions_chain.actions
        if action.function._function == action_function
    ]


def _get_inputs_of_filters(page: Page, action_function:  Callable[[Any], Dict[str, Any]]) -> List[State]:
    """Gets list of `States` for selected `control_type` of triggered `Page`."""
    filter_actions_on_page = _get_matching_actions_by_function(
        page_id=ModelID(str(page.id)), action_function=action_function
    )
    inputs = []
    for action in filter_actions_on_page:
        triggered_model = model_manager._get_action_trigger(action_id=ModelID(str(action.id)))
        inputs.append(
            State(component_id=triggered_model.id, component_property=triggered_model._input_property)
        )

    return inputs


def _get_inputs_of_figure_interactions(
    page: Page, action_function: Callable[[Any], Dict[str, Any]]
) -> List[Dict[str, State]]:
    """Gets list of `States` for selected chart interaction `action_function` of triggered `Page`."""
    figure_interactions_on_page = _get_matching_actions_by_function(
        page_id=ModelID(str(page.id)), action_function=action_function
    )
    inputs = []
    for action in figure_interactions_on_page:
        triggered_model = model_manager._get_action_trigger(action_id=ModelID(str(action.id)))
        if isinstance(triggered_model, vm.Table):
            inputs.append(
                {
                    "active_cell": State(
                        component_id=triggered_model._callable_object_id, component_property="active_cell"
                    ),
                    "derived_viewport_data": State(
                        component_id=triggered_model._callable_object_id, component_property="derived_viewport_data"
                    ),
                }
            )
        else:
            inputs.append({"clickData": State(component_id=triggered_model.id, component_property="clickData")})

    return inputs


class ExportOriginalData(CapturedActionCallable):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        # Fake initialization
        super().__init__(*args, **kwargs)

    def _post_init(self):
        self._page_id = model_manager._get_model_page_id(model_id=self._action_id)

        # Validate and calculate "targets"
        targets = self._kwargs.get("targets")
        if targets:
            for target in targets:
                if target not in model_manager:
                    raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        else:
            targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        self._kwargs["targets"] = self.targets = targets

        # Validate and calculate "file_format"
        file_format = self._kwargs.get("file_format", "csv")
        if file_format not in ["csv", "xlsx"]:
            raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
        if file_format == "xlsx":
            if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                raise ModuleNotFoundError(
                    "You must install either openpyxl or xlsxwriter to export to xlsx format."
                )
        self._kwargs["file_format"] = self.file_format = file_format

        # post initialization
        super().__init__(*self._args, **self._kwargs)

    @staticmethod
    def pure_function(
        targets: List[str],
        file_format: Literal["csv", "xlsx"] = "csv",
        **inputs: Dict[str, Any]
    ):
        data_frames = _get_filtered_data(
            targets=targets,
            ctds_filters=ctx.args_grouping["external"]["filters"],
            ctds_filter_interaction=ctx.args_grouping["external"]["filter_interaction"],
        )

        outputs = {}
        for target_id in targets:
            if file_format == "csv":
                writer = data_frames[target_id].to_csv
            elif file_format == "xlsx":
                writer = data_frames[target_id].to_excel

            outputs[f"download_dataframe_{target_id}"] = dcc.send_data_frame(
                writer=writer, filename=f"{target_id}.{file_format}", index=False
            )

        return outputs

    @property
    def inputs(self):
        # TODO: Go with _get_inputs_of_figure_interactions for every input. It fetched filter/parameters inputs from every components.
        # TODO: Do more refactoring: Take the _actions_info into account,

        page = model_manager[self._page_id]
        return {
            "filters": _get_inputs_of_filters(
                page=page,
                action_function=_filter.__wrapped__
            ),
            "filter_interaction": _get_inputs_of_figure_interactions(
                page=page,
                action_function=filter_interaction.__wrapped__
            ),
            # TODO: Try not to propagate this if theme_selector is overwritten and not the part of the page.
            "theme_selector": State("theme_selector", "checked"),
        }

    @property
    def outputs(self) -> Dict[str, Output]:
        """Gets mapping of relevant output target name and `Outputs` for `export_data` action."""
        return {
            f"download_dataframe_{target}": Output(
                component_id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target},
                component_property="data",
            )
            for target in self.targets
        }

    @property
    def components(self):
        """Creates dcc.Downloads for target components of the `export_data` action."""
        return [
            dcc.Download(id={"type": "download_dataframe", "action_id": self._action_id, "target_id": target})
            for target in self.targets
        ]


# Alias for ExportOriginalData
export_original_data = ExportOriginalData
