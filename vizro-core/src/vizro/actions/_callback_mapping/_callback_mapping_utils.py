"""Contains utilities to create the action_callback_mapping."""

from collections.abc import Iterable
from typing import Any, Callable, cast

from dash import State

from vizro.actions import filter_interaction
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, Page, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain
from vizro.models.types import ControlType

# tODO: finish tidying/removing this file depending on where functionality is used. e.g. in CapturedActionCallable


# This function can also be reused for all other inputs (filters, parameters).
# Potentially this could be a way to reconcile predefined with custom actions,
# and make that predefined actions see and add into account custom actions.
def _get_matching_actions_by_function(page: Page, action_function: Callable[[Any], dict[str, Any]]) -> list[Action]:
    """Gets list of `Actions` on triggered `Page` that match the provided `action_function`."""
    return [
        action
        for actions_chain in cast(Iterable[ActionsChain], model_manager._get_models(ActionsChain, page))
        for action in actions_chain.actions
        if action.function._function == action_function
    ]


# CALLBACK STATES --------------
def _get_inputs_of_controls(page: Page, control_type: ControlType) -> list[State]:
    """Gets list of `States` for selected `control_type` of triggered `Page`."""
    return [
        State(component_id=control.selector.id, component_property=control.selector._input_property)
        for control in cast(Iterable[ControlType], model_manager._get_models(control_type, page))
    ]


def _get_action_trigger(action: Action) -> VizroBaseModel:  # type: ignore[return]
    """Gets the model that triggers the action with "action_id"."""
    from vizro.models._action._actions_chain import ActionsChain

    for actions_chain in cast(Iterable[ActionsChain], model_manager._get_models(ActionsChain)):
        if action in actions_chain.actions:
            return model_manager[ModelID(str(actions_chain.trigger.component_id))]


def _get_inputs_of_figure_interactions(page: Page) -> list[dict[str, State]]:
    """Gets list of `States` for selected chart interaction `action_function` of triggered `Page`."""
    figure_interactions_on_page = _get_matching_actions_by_function(
        page_id=ModelID(str(page.id)), action_function=filter_interaction.function
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
