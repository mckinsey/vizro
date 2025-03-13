"""Contains utilities to create the action_callback_mapping."""

from collections.abc import Iterable
from typing import Any, Callable, Union, cast

from dash import Output, State, dcc

from vizro.actions import _parameter, filter_interaction
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, ModelID
from vizro.models import Action, Page, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls import Filter, Parameter
from vizro.models.types import ControlType


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


def _get_inputs_of_figure_interactions(
    page: Page, action_function: Callable[[Any], dict[str, Any]]
) -> list[dict[str, State]]:
    """Gets list of `States` for selected chart interaction `action_function` of triggered `Page`."""
    figure_interactions_on_page = _get_matching_actions_by_function(page=page, action_function=action_function)
    inputs = []
    for action in figure_interactions_on_page:
        triggered_model = _get_action_trigger(action)
        required_attributes = ["_filter_interaction_input", "_filter_interaction"]
        for attribute in required_attributes:
            if not hasattr(triggered_model, attribute):
                raise ValueError(f"Model {triggered_model.id} does not have required attribute `{attribute}`.")
        if "modelID" not in triggered_model._filter_interaction_input:  # type: ignore[attr-defined]
            raise ValueError(
                f"Model {triggered_model.id} does not have required State `modelID` in `_filter_interaction_input`."
            )
        inputs.append(triggered_model._filter_interaction_input)  # type: ignore[attr-defined]
    return inputs


# TODO: Refactor this and util functions once we implement "_get_input_property" method in VizroBaseModel models
def _get_action_callback_inputs(action: Action) -> dict[str, list[Union[State, dict[str, State]]]]:
    """Creates mapping of pre-defined action names and a list of `States`."""
    page = model_manager._get_model_page(action)

    action_input_mapping = {
        "filters": _get_inputs_of_controls(page=page, control_type=Filter),
        "parameters": _get_inputs_of_controls(page=page, control_type=Parameter),
        # TODO: Probably need to adjust other inputs to follow the same structure list[dict[str, State]]
        "filter_interaction": _get_inputs_of_figure_interactions(
            page=page, action_function=filter_interaction.__wrapped__
        ),
    }
    return action_input_mapping


# CALLBACK OUTPUTS --------------
def _get_action_callback_outputs(action: Action) -> dict[str, Output]:
    """Creates mapping of target names and their `Output`."""
    action_function = action.function._function

    # The right solution for mypy here is to not e.g. define new attributes on the base but instead to get mypy to
    # recognize that model_manager[action_id] is of type Action and hence has the function attribute.
    # Ideally model_manager.__getitem__ would handle this itself, possibly with suitable use of a cast.
    # If not then we can do the cast to Action at the point of consumption here to avoid needing mypy ignores.

    try:
        targets = action.function["targets"]
    except KeyError:
        targets = []

    if action_function == _parameter.__wrapped__:
        # Targets without "." are implicitly added by the `Parameter._set_actions` method
        # to handle cases where a dynamic data parameter affects a filter or its targets.
        targets = [target.split(".")[0] if "." in target else target for target in targets]

    return {
        target: Output(
            component_id=target,
            component_property=model_manager[target]._output_component_property,  # type: ignore[attr-defined]
            allow_duplicate=True,
        )
        for target in targets
    }


def _get_export_data_callback_outputs(action: Action) -> dict[str, Output]:
    """Gets mapping of relevant output target name and `Outputs` for `export_data` action."""
    try:
        targets = action.function["targets"]
    except KeyError:
        targets = None

    targets = targets or [
        model.id
        for model in cast(
            Iterable[VizroBaseModel], model_manager._get_models(FIGURE_MODELS, model_manager._get_model_page(action))
        )
    ]

    return {
        f"download_dataframe_{target}": Output(
            component_id={"type": "download_dataframe", "action_id": action.id, "target_id": target},
            component_property="data",
        )
        for target in targets
    }


# CALLBACK COMPONENTS --------------
def _get_export_data_callback_components(action: Action) -> list[dcc.Download]:
    """Creates dcc.Downloads for target components of the `export_data` action."""
    try:
        targets = action.function["targets"]
    except KeyError:
        targets = None

    targets = targets or [
        model.id
        for model in cast(
            Iterable[VizroBaseModel], model_manager._get_models(FIGURE_MODELS, model_manager._get_model_page(action))
        )
    ]

    return [
        dcc.Download(id={"type": "download_dataframe", "action_id": action.id, "target_id": target})
        for target in targets
    ]
