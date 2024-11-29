"""Contains utilities to create the action_callback_mapping."""

from typing import Any, Callable

from dash import State

from vizro.actions import filter_interaction
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, Page
from vizro.models.types import ControlType


# This function can also be reused for all other inputs (filters, parameters).
# Potentially this could be a way to reconcile predefined with custom actions,
# and make that predefined actions see and add into account custom actions.
def _get_matching_actions_by_function(
    page_id: ModelID, action_function: Callable[[Any], dict[str, Any]]
) -> list[Action]:
    """Gets list of `Actions` on triggered `Page` that match the provided `action_function`."""
    return [
        action
        for actions_chain in model_manager._get_page_actions_chains(page_id=page_id)
        for action in actions_chain.actions
        if action.function._function == action_function
    ]


# CALLBACK STATES --------------
def _get_inputs_of_controls(page: Page, control_type: ControlType) -> list[State]:
    """Gets list of `States` for selected `control_type` of triggered `Page`."""
    return [
        State(component_id=control.selector.id, component_property=control.selector._input_property)
        for control in page.controls
        if isinstance(control, control_type)
    ]


def _get_inputs_of_figure_interactions(page: Page) -> list[dict[str, State]]:
    """Gets list of `States` for selected chart interaction `action_function` of triggered `Page`."""
    figure_interactions_on_page = _get_matching_actions_by_function(
        page_id=ModelID(str(page.id)), action_function=filter_interaction.pure_function
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


# THIS UTILS FILE IS ONLY ASSOCIATED WITH ACTIONS NOW SO SHOULD GO THERE
# This assumes that we can supply inputs automatically to all callbacks that don't have inputs defined manually.
