"""Contains utilities to create the action_callback_mapping."""

from itertools import chain
from typing import Any, Callable, Dict, List, NamedTuple

from dash import Output, State, dcc

from vizro.actions import _on_page_load, _parameter, export_data, filter_interaction
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, Page, Table, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls import Filter, Parameter
from vizro.models.types import ControlType


class ModelActionsChains(NamedTuple):
    model: VizroBaseModel
    actions_chains: List[ActionsChain]


def _get_actions(model) -> List[ActionsChain]:
    """Gets the list of trigger action chains in the `action` parameter for any model."""
    if hasattr(model, "selector"):
        return model.selector.actions
    elif hasattr(model, "actions"):
        return model.actions
    return []


def _get_all_actions_chains_on_page(page: Page) -> chain:  # type: ignore[type-arg]
    """Creates an itertools chain of all ActionsChains present on selected Page."""
    return chain(*(_get_actions(page_item) for page_item in chain([page], page.components, page.controls)))


def _get_model_actions_chains_mapping(page: Page) -> Dict[str, ModelActionsChains]:
    """Creates a mapping of model ids and ModelActionsChains for selected Page."""
    model_actions_chains_mapping = {}
    for page_item in chain([page], page.components, page.controls):
        model_actions_chains_mapping[page_item.id] = ModelActionsChains(
            model=page_item, actions_chains=_get_actions(page_item)
        )
    return model_actions_chains_mapping


def _get_triggered_page(action_id: ModelID) -> Page:  # type: ignore[return]
    """Gets the page where the provided `action_id` has been triggered."""
    for _, page in model_manager._items_with_type(Page):
        if any(
            action.id == action_id
            for actions_chain in _get_all_actions_chains_on_page(page)
            for action in actions_chain.actions
        ):
            return page


def _get_triggered_model(action_id: ModelID) -> VizroBaseModel:  # type: ignore[return]
    """Gets the model where the provided `action_id` has been triggered."""
    for _, page in model_manager._items_with_type(Page):
        for model_id, model_actions_chains in _get_model_actions_chains_mapping(page).items():
            if any(
                action.id == action_id
                for actions_chain in model_actions_chains.actions_chains
                for action in actions_chain.actions
            ):
                return model_actions_chains.model


def _get_components_with_data(action_id: ModelID) -> List[str]:
    """Gets all components that have a registered dataframe on the page where `action_id` was triggered."""
    page = _get_triggered_page(action_id=action_id)
    return [component.id for component in page.components if data_manager._has_registered_data(component.id)]


def _get_matching_actions_by_function(page: Page, action_function: Callable[[Any], Dict[str, Any]]) -> List[Action]:
    """Gets list of Actions on triggered page that match the provided action function."""
    return [
        action
        for actions_chain in _get_all_actions_chains_on_page(page)
        for action in actions_chain.actions
        if action.function._function == action_function
    ]


# CALLBACK STATES --------------
def _get_inputs_of_controls(action_id: ModelID, control_type: ControlType) -> List[State]:
    """Gets list of States for selected control_type of triggered page."""
    page = _get_triggered_page(action_id=action_id)
    return [
        State(
            component_id=control.selector.id,
            component_property=control.selector._input_property,
        )
        for control in page.controls
        if isinstance(control, control_type)
    ]


def _get_inputs_of_figure_interactions(
    action_id: ModelID, action_function: Callable[[Any], Dict[str, Any]]
) -> List[Dict[str, State]]:
    """Gets list of States for selected chart interaction `action_name` of triggered page."""
    figure_interactions_on_page = _get_matching_actions_by_function(
        page=_get_triggered_page(action_id=action_id),
        action_function=action_function,
    )
    inputs = []
    for action in figure_interactions_on_page:
        # TODO: Consider do we want to move the following logic into Model implementation
        triggered_model = _get_triggered_model(action_id=ModelID(str(action.id)))
        if isinstance(triggered_model, Table):
            inputs.append(
                {
                    "active_cell": State(
                        component_id=triggered_model._callable_object_id, component_property="active_cell"
                    ),
                    "derived_viewport_data": State(
                        component_id=triggered_model._callable_object_id,
                        component_property="derived_viewport_data",
                    ),
                }
            )
        else:
            inputs.append(
                {
                    "clickData": State(component_id=triggered_model.id, component_property="clickData"),
                }
            )

    return inputs


def _get_action_callback_inputs(action_id: ModelID) -> Dict[str, Any]:
    """Creates mapping of pre-defined action names and a list of States."""
    action_function = model_manager[action_id].function._function  # type: ignore[attr-defined]

    if action_function == export_data.__wrapped__:
        include_inputs = ["filters", "filter_interaction"]
    else:
        include_inputs = ["filters", "parameters", "filter_interaction", "theme_selector"]

    action_input_mapping = {
        "filters": (
            _get_inputs_of_controls(action_id=action_id, control_type=Filter) if "filters" in include_inputs else []
        ),
        "parameters": (
            _get_inputs_of_controls(action_id=action_id, control_type=Parameter)
            if "parameters" in include_inputs
            else []
        ),
        # TODO: Probably need to adjust other inputs to follow the same structure List[Dict[str, State]]
        "filter_interaction": (
            _get_inputs_of_figure_interactions(action_id=action_id, action_function=filter_interaction.__wrapped__)
            if "filter_interaction" in include_inputs
            else []
        ),
        "theme_selector": (State("theme_selector", "on") if "theme_selector" in include_inputs else []),
    }
    return action_input_mapping


# CALLBACK OUTPUTS --------------
def _get_action_callback_outputs(action_id: ModelID) -> Dict[str, Output]:
    """Creates mapping of target names and their Output."""
    action_function = model_manager[action_id].function._function  # type: ignore[attr-defined]

    # The right solution for mypy here is to not e.g. define new attributes on the base but instead to get mypy to
    # recognize that model_manager[action_id] is of type Action and hence has the function attribute.
    # Ideally model_manager.__getitem__ would handle this itself, possibly with suitable use of a cast.
    # If not then we can do the cast to Action at the point of consumption here to avoid needing mypy ignores.

    try:
        targets = model_manager[action_id].function["targets"]  # type: ignore[attr-defined]
    except KeyError:
        targets = []

    if action_function == _parameter.__wrapped__:
        targets = [target.split(".")[0] for target in targets]

    if action_function == _on_page_load.__wrapped__:
        targets = _get_components_with_data(action_id=action_id)

    return {
        target: Output(
            component_id=target,
            component_property=model_manager[target]._output_property,  # type: ignore[attr-defined]
            allow_duplicate=True,
        )
        for target in targets
    }


def _get_export_data_callback_outputs(action_id: ModelID) -> Dict[str, List[State]]:
    """Gets mapping of relevant output target name and Outputs for `export_data` action."""
    action = model_manager[action_id]

    try:
        targets = action.function["targets"]  # type: ignore[attr-defined]
    except KeyError:
        targets = None

    if not targets:
        targets = _get_components_with_data(action_id=action_id)

    return {
        f"download-dataframe_{target}": Output(
            component_id={
                "type": "download-dataframe",
                "action_id": action_id,
                "target_id": target,
            },
            component_property="data",
        )
        for target in targets
    }


# CALLBACK COMPONENTS --------------
def _get_export_data_callback_components(action_id: ModelID) -> List[dcc.Download]:
    """Creates dcc.Downloads for target components of the `export_data` action."""
    action = model_manager[action_id]

    try:
        targets = action.function["targets"]  # type: ignore[attr-defined]
    except KeyError:
        targets = None

    if not targets:
        targets = _get_components_with_data(action_id=action_id)

    return [
        dcc.Download(
            id={
                "type": "download-dataframe",
                "action_id": action_id,
                "target_id": target,
            },
        )
        for target in targets
    ]
