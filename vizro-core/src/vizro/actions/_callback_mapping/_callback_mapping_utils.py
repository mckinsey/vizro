"""Contains utilities to create the action_callback_mapping."""

from typing import Dict, List

from dash import State

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, Page
from vizro.models.types import CapturedActionCallable


def _get_matching_page_actions_by_action_class(
    page_id: ModelID,
    action_class: CapturedActionCallable,
) -> List[Action]:
    """Gets list of `Actions` on triggered `Page` that match the provided `action_class`."""
    return [
        action
        for actions_chain in model_manager._get_page_actions_chains(page_id=page_id)
        for action in actions_chain.actions
        if isinstance(action.function, action_class)
    ]


# TODO-AV2-TICKET: Once "actions_info" is implemented, functions like:
#  _get_inputs_of_filters, _get_inputs_of_parameters, _get_inputs_of_figure_interactions will become a single function.
def _get_inputs_of_filters(page: Page, action_class: CapturedActionCallable = None) -> List[State]:
    """Gets list of `States` for all components that have the `filter` action from the `Page`."""
    filter_actions_on_page = _get_matching_page_actions_by_action_class(
        page_id=ModelID(str(page.id)), action_class=action_class
    )
    inputs = []
    # TODO-AV2-TICKET: Take the "actions_info" into account once it's implemented.
    for action in filter_actions_on_page:
        triggered_model = model_manager._get_action_trigger(action_id=ModelID(str(action.id)))
        inputs.append(State(component_id=triggered_model.id, component_property=triggered_model._input_property))

    return inputs


def _get_inputs_of_parameters(page: Page, action_class: CapturedActionCallable = None) -> List[State]:
    """Gets list of `States` for all components that have the `parameter` action from the `Page`."""
    parameter_actions_on_page = _get_matching_page_actions_by_action_class(
        page_id=ModelID(str(page.id)), action_class=action_class
    )
    inputs = []
    # TODO-AV2-TICKET: Take the "actions_info" into account once it's implemented.
    for action in parameter_actions_on_page:
        triggered_model = model_manager._get_action_trigger(action_id=ModelID(str(action.id)))
        inputs.append(State(component_id=triggered_model.id, component_property=triggered_model._input_property))

    return inputs


def _get_inputs_of_figure_interactions(
    page: Page, action_class: CapturedActionCallable = None
) -> List[Dict[str, State]]:
    """Gets list of `States` for selected chart interaction `action_function` of triggered `Page`."""
    figure_interactions_on_page = _get_matching_page_actions_by_action_class(
        page_id=ModelID(str(page.id)), action_class=action_class
    )
    inputs = []
    # TODO-AV2-TICKET: Take the "actions_info" into account once it's implemented.
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
