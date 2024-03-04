from __future__ import annotations
import abc

from vizro.models.types import capture, CapturedCallable
from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, List, Optional
from dash import ctx, dcc, Output, State

from vizro.actions import filter_interaction
from vizro.actions._filter_action import _filter
from vizro.managers import data_manager, model_manager

if TYPE_CHECKING:
    from vizro.models import Page
    from vizro.models import Filter
    from vizro.models._models import ModelID
    from vizro.models._table import Table

from vizro.models import VizroBaseModel
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
import importlib
from vizro.managers._model_manager import ModelID
from vizro._constants import ALL_OPTION, NONE_OPTION
import vizro.models as vm




def pure_f(a: int, b: int) -> int:
    return a + b


f1 = capture("action")(pure_f)

# Above is same as
# @capture("action")
# def f1(a: int, b: int) -> int:
#     return a + b

# calling f1() returns CapturedCallable
# So do f1()(1, 2) or f1(1, 2)() or f1(1)(2) etc. to actually get a + b


class CapturedActionCallable(CapturedCallable, abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(self.pure_function, *args, **kwargs)

    @staticmethod
    @abc.abstractmethod
    # Maybe need to have self so can access inputs/outputs/components?
    # If not then, keep as staticmethod.
    # Call it just function, no underscores.
    def pure_function(a, b):
        return a + b

    # Should these also be abstract? Probably not.
    # Should they be class properties? Maybe.
    # Will you ever need self in them? Maybe.
    @property
    def inputs(self):
        return []

    @property
    def outputs(self):
        return []

    @property
    def components(self):
        # Do we really need this? Should it return an empty list?
        return []




# Need @functools.wraps for this to work nicely with docstring etc., but that's not so important
# Will have one class per action
# f2 operates same way as f1, so f2() returns a CapturedCallable
class f2(CapturedActionCallable):
    @staticmethod
    def pure_function(a, b):
        return a + b

    @property
    def inputs(self):
       return ["a", "b"]


def _get_component_actions(component) -> List[Action]:
    return (
        [action for actions_chain in component.actions for action in actions_chain.actions]
        if hasattr(component, "actions")
        else []
    )

def _apply_filters(data_frame: pd.DataFrame, ctds_filters: List[CallbackTriggerDict], target: str) -> pd.DataFrame:
    for ctd in ctds_filters:
        selector_value = ctd["value"]
        selector_value = selector_value if isinstance(selector_value, list) else [selector_value]
        selector_actions = _get_component_actions(model_manager[ctd["id"]])

        for action in selector_actions:
            if (
                action.function._function.__name__ != "_filter"
                or target not in action.function["targets"]
                or ALL_OPTION in selector_value
            ):
                continue

            _filter_function = action.function["filter_function"]
            _filter_column = action.function["filter_column"]
            _filter_value = selector_value
            data_frame = data_frame[_filter_function(data_frame[_filter_column], _filter_value)]

    return data_frame


def _apply_graph_filter_interaction(
    data_frame: pd.DataFrame, target: str, ctd_filter_interaction: Dict[str, CallbackTriggerDict]
) -> pd.DataFrame:
    ctd_click_data = ctd_filter_interaction["clickData"]
    if not ctd_click_data["value"]:
        return data_frame

    source_graph_id: ModelID = ctd_click_data["id"]
    source_graph_actions = _get_component_actions(model_manager[source_graph_id])
    try:
        custom_data_columns = model_manager[source_graph_id]["custom_data"]
    except KeyError as exc:
        raise KeyError(f"No `custom_data` argument found for source graph with id {source_graph_id}.") from exc

    customdata = ctd_click_data["value"]["points"][0]["customdata"]

    for action in source_graph_actions:
        if action.function._function.__name__ != "filter_interaction" or target not in action.function["targets"]:
            continue
        for custom_data_idx, column in enumerate(custom_data_columns):
            data_frame = data_frame[data_frame[column].isin([customdata[custom_data_idx]])]

    return data_frame

def _apply_filter_interaction(
    data_frame: pd.DataFrame, ctds_filter_interaction: List[Dict[str, CallbackTriggerDict]], target: str
) -> pd.DataFrame:
    for ctd_filter_interaction in ctds_filter_interaction:
        if "clickData" in ctd_filter_interaction:
            data_frame = _apply_graph_filter_interaction(
                data_frame=data_frame, target=target, ctd_filter_interaction=ctd_filter_interaction
            )

        if "active_cell" in ctd_filter_interaction and "derived_viewport_data" in ctd_filter_interaction:
            data_frame = _apply_table_filter_interaction(
                data_frame=data_frame, target=target, ctd_filter_interaction=ctd_filter_interaction
            )

    return data_frame


def _get_filtered_data(
    targets: List[ModelID],
    ctds_filters: List[CallbackTriggerDict],
    ctds_filter_interaction: List[Dict[str, CallbackTriggerDict]],
) -> Dict[ModelID, pd.DataFrame]:
    filtered_data = {}
    for target in targets:
        data_frame = data_manager._get_component_data(target)

        data_frame = _apply_filters(data_frame=data_frame, ctds_filters=ctds_filters, target=target)
        data_frame = _apply_filter_interaction(
            data_frame=data_frame, ctds_filter_interaction=ctds_filter_interaction, target=target
        )

        filtered_data[target] = data_frame

    return filtered_data


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
        if not targets:
            targets = model_manager._get_page_model_ids_with_figure(page_id=self._page_id)
        else:
            for target in targets:
                if target not in model_manager:
                    raise ValueError(f"Component '{target}' does not exist on the page '{self._page_id}'.")
        self.targets = targets
        self._kwargs["targets"] = targets

        # Validate and calculate "file_format"
        file_format = self._kwargs.get("file_format", "csv")
        if file_format not in ["csv", "xlsx"]:
            raise ValueError(f'Unknown "file_format": {file_format}.' f' Known file formats: "csv", "xlsx".')
        if file_format == "xlsx":
            if importlib.util.find_spec("openpyxl") is None and importlib.util.find_spec("xlsxwriter") is None:
                raise ModuleNotFoundError(
                    "You must install either openpyxl or xlsxwriter to export to xlsx format."
                )
        self.file_format = file_format
        self._kwargs["file_format"] = file_format

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







# Use an existing action inside a new one
def pure_g(a: int, b: int) -> int:
    # Or f2()._function() works
    # f2.__wrapped__ doesn't work since don't have functools.wraps
    # Maybe make a helper function to make this look less weird
    # But no way to just do as f2(1, 2) or wouldn't work when you use that as a standalone action
    return 2 * f2(a, b)()


g1 = capture("action")(pure_g)
# Above is same as
# @capture("action")
# def g1(a: int, b: int) -> int:
#     return 2 * f2(a, b)()


# Advanced user could do this
class g2(f2):
    @staticmethod
    def pure_function(a, b):
        # Need to do super(g2, g2) or specify f2 explicitly as in staticmethod.
        return 2 * f2.pure_function(a, b)

    # def inputs(self):
    #    return ...


# Do this for actions but not tables - for that have separate models and also modes

# Should we alter capture("action") to return CapturedActionCallable?

# How to do:
# Do change for simplest action, review it
# Look again at Action model and how to handle inputs/outputs, whether to move anything from Action into CapturedActionCallable
# Then roll out to all actions
# Try to remove CapturedCallable._function
# Then look at next bits of refactoring e.g. on_page_load - bits might need to change again, but sure that this is step
# in right direction
