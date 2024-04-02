"""Contains utilities to create the action_callback_mapping."""

from typing import Any, Callable, Dict, List, Union

from dash import Output, State, dcc

from vizro.actions import _parameter, export_data, filter_interaction
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, Page
from vizro.models._controls import Filter, Parameter
from vizro.models.types import ControlType


# This function can also be reused for all other inputs (filters, parameters).
# Potentially this could be a way to reconcile predefined with custom actions,
# and make that predefined actions see and add into account custom actions.
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


# CALLBACK STATES --------------
def _get_inputs_of_controls(page: Page, control_type: ControlType) -> List[State]:
    """Gets list of `States` for selected `control_type` of triggered `Page`."""
    return [
        State(component_id=control.selector.id, component_property=control.selector._input_property)
        for control in page.controls
        if isinstance(control, control_type)
    ]


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
        required_attributes = ["_filter_interaction_input", "_filter_interaction"]
        for attribute in required_attributes:
            if not hasattr(triggered_model, attribute):
                raise ValueError(f"Model {triggered_model.id} does not have required attribute `{attribute}`.")
        if "modelID" not in triggered_model._filter_interaction_input:
            raise ValueError(
                f"Model {triggered_model.id} does not have required State `modelID` in `_filter_interaction_input`."
            )
        inputs.append(triggered_model._filter_interaction_input)
    return inputs


# TODO: Refactor this and util functions once we implement "_get_input_property" method in VizroBaseModel models
def _get_action_callback_inputs(action_id: ModelID) -> Dict[str, List[Union[State, Dict[str, State]]]]:
    """Creates mapping of pre-defined action names and a list of `States`."""
    action_function = model_manager[action_id].function._function
    page: Page = model_manager[model_manager._get_model_page_id(model_id=action_id)]

    if action_function == export_data.__wrapped__:
        include_inputs = ["filters", "filter_interaction"]
    else:
        include_inputs = ["filters", "parameters", "filter_interaction", "theme_selector"]

    action_input_mapping = {
        "filters": (_get_inputs_of_controls(page=page, control_type=Filter) if "filters" in include_inputs else []),
        "parameters": (
            _get_inputs_of_controls(page=page, control_type=Parameter) if "parameters" in include_inputs else []
        ),
        # TODO: Probably need to adjust other inputs to follow the same structure List[Dict[str, State]]
        "filter_interaction": (
            _get_inputs_of_figure_interactions(page=page, action_function=filter_interaction.__wrapped__)
            if "filter_interaction" in include_inputs
            else []
        ),
        "theme_selector": State("theme_selector", "checked") if "theme_selector" in include_inputs else [],
    }
    return action_input_mapping


# CALLBACK OUTPUTS --------------
def _get_action_callback_outputs(action_id: ModelID) -> Dict[str, Output]:
    """Creates mapping of target names and their `Output`."""
    action_function = model_manager[action_id].function._function

    # The right solution for mypy here is to not e.g. define new attributes on the base but instead to get mypy to
    # recognize that model_manager[action_id] is of type Action and hence has the function attribute.
    # Ideally model_manager.__getitem__ would handle this itself, possibly with suitable use of a cast.
    # If not then we can do the cast to Action at the point of consumption here to avoid needing mypy ignores.

    try:
        targets = model_manager[action_id].function["targets"]
    except KeyError:
        targets = []

    if action_function == _parameter.__wrapped__:
        targets = [target.split(".")[0] for target in targets]

    return {
        target: Output(
            component_id=target,
            component_property=model_manager[target]._output_component_property,
            allow_duplicate=True,
        )
        for target in targets
    }


def _get_export_data_callback_outputs(action_id: ModelID) -> Dict[str, Output]:
    """Gets mapping of relevant output target name and `Outputs` for `export_data` action."""
    action = model_manager[action_id]

    try:
        targets = action.function["targets"]
    except KeyError:
        targets = None

    if not targets:
        targets = model_manager._get_page_model_ids_with_figure(
            page_id=model_manager._get_model_page_id(model_id=action_id)
        )

    return {
        f"download_dataframe_{target}": Output(
            component_id={"type": "download_dataframe", "action_id": action_id, "target_id": target},
            component_property="data",
        )
        for target in targets
    }


# CALLBACK COMPONENTS --------------
def _get_export_data_callback_components(action_id: ModelID) -> List[dcc.Download]:
    """Creates dcc.Downloads for target components of the `export_data` action."""
    action = model_manager[action_id]

    try:
        targets = action.function["targets"]
    except KeyError:
        targets = None

    if not targets:
        targets = model_manager._get_page_model_ids_with_figure(
            page_id=model_manager._get_model_page_id(model_id=action_id)
        )

    return [
        dcc.Download(id={"type": "download_dataframe", "action_id": action_id, "target_id": target})
        for target in targets
    ]
