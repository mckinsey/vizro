"""Contains utilities for the implementation of callbacks."""
import json
import logging
from itertools import chain
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union

from dash import Input, Output, State, callback, clientside_callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import _filter, _on_page_load, _parameter, action_functions, export_data, filter_interaction
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Page, VizroBaseModel
from vizro.models._action._action import Action
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls import Filter, Parameter
from vizro.models.types import ControlType

logger = logging.getLogger(__name__)


class ModelActionsChains(NamedTuple):
    model: VizroBaseModel
    actions_chains: List[ActionsChain]


# CALLBACK HELPER FUNCTIONS --------------
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


# CALLBACK STORES -----------------------
# TODO - Return only components for selected dashboard pages (not for all)
def _get_actions_components() -> List[Union[dcc.Store, html.Div, dcc.Download]]:
    # TODO - Refactor the entire function
    actions_chains = [actions_chain for _, actions_chain in model_manager._items_with_type(ActionsChain)]
    actions = [action for _, action in model_manager._items_with_type(Action)]

    components = [
        dcc.Store(id="empty_input_store"),
        dcc.Store(id="empty_output_store"),
        dcc.Store(id="action_finished"),
        dcc.Store(id="set_remaining"),
        dcc.Store(id="remaining_actions"),
        html.Div(id="cycle_breaker_div", style={"display": "hidden"}),
        dcc.Store(id="cycle_breaker_empty_output_store"),
    ]

    components.extend(
        [
            dcc.Store(
                id={"type": "gateway_input", "trigger_id": actions_chain.id},
                data=f"{actions_chain.id}",
            )
            for actions_chain in actions_chains
        ]
    )

    components.extend(component for action in actions for component in action._get_components())

    for page_id, page in model_manager._items_with_type(Page):
        components.append(
            dcc.Store(
                id={"type": "gateway_input", "trigger_id": f"page-{page_id}"},
                data=f"page-{page_id}",
            )
        )

    return components


# CALLBACK STATES --------------
def _get_inputs_of_controls(action_id: ModelID, control_type: ControlType) -> List[State]:
    """Gets list of States for selected control_type of triggered page."""
    page = _get_triggered_page(action_id=action_id)
    return [
        State(
            component_id=control.selector.id,
            component_property="value",
        )
        for control in page.controls
        if isinstance(control, control_type)
    ]


def _get_inputs_of_chart_interactions(
    action_id: ModelID, action_function: Callable[[Any], Dict[str, Any]]
) -> List[State]:
    """Gets list of States for selected chart interaction `action_name` of triggered page."""
    chart_interactions_on_page = _get_matching_actions_by_function(
        page=_get_triggered_page(action_id=action_id),
        action_function=action_function,
    )
    return [
        State(
            component_id=_get_triggered_model(action_id=action.id).id,  # type: ignore[arg-type]
            component_property="clickData",
        )
        for action in chart_interactions_on_page
    ]


def _get_action_callback_inputs(action_id: ModelID) -> Dict[str, List[State]]:
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
        "filter_interaction": (
            _get_inputs_of_chart_interactions(action_id=action_id, action_function=filter_interaction.__wrapped__)
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
            component_property="figure",
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


# CALLBACK MAPPING --------------
def _get_action_callback_mapping(action_id: ModelID, argument: str) -> Dict[str, Union[Input, State, Output]]:
    """Creates mapping of action name and required callback input/output."""
    action_function = model_manager[action_id].function._function  # type: ignore[attr-defined]

    action_callback_mapping: Dict[str, Any] = {
        export_data.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "components": _get_export_data_callback_components,
            "outputs": _get_export_data_callback_outputs,
        },
        _filter.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        filter_interaction.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        _parameter.__wrapped__: {
            "inputs": _get_action_callback_inputs,
            "outputs": _get_action_callback_outputs,
        },
        _on_page_load.__wrapped__: {"inputs": _get_action_callback_inputs, "outputs": _get_action_callback_outputs},
    }
    action_call = action_callback_mapping.get(action_function, {}).get(argument, {})
    return action_call if isinstance(action_call, dict) else action_call(action_id=action_id)


# makes callbacks that enable actions engine-loop mechanism to work
# + one callback per action
def _make_app_callbacks() -> None:
    # TODO - Refactor the entire function
    actions_chains = [actions_chain for _, actions_chain in model_manager._items_with_type(ActionsChain)]
    actions = [action for _, action in model_manager._items_with_type(Action)]

    gateway_triggers: List[Input] = []
    for actions_chain in actions_chains:

        @callback(
            Output({"type": "gateway_input", "trigger_id": actions_chain.id}, "data"),
            Input(
                component_id=actions_chain.trigger.component_id,
                component_property=actions_chain.trigger.component_property,
            ),
            State({"type": "gateway_input", "trigger_id": actions_chain.id}, "data"),
            prevent_initial_call=True,
        )
        def trigger_to_global_store(_, data):
            return data

        gateway_triggers.append(
            Input(
                component_id={"type": "gateway_input", "trigger_id": actions_chain.id},
                component_property="data",
            )
        )

    # TODO: don't create any components or callback if there's no actions configured
    if not gateway_triggers:
        gateway_triggers.append(Input("empty_input_store", "data"))

    action_triggers = [Output({"type": "action_trigger", "action_name": action.id}, "data") for action in actions]
    if not action_triggers:
        action_triggers.append(Output("empty_output_store", "data", allow_duplicate=True))

    # gateway
    @callback(
        Output("set_remaining", "data"),
        gateway_triggers,
        prevent_initial_call=True,
    )
    def gateway(*gateway_triggers: List[dcc.Store]) -> List[Optional[str]]:
        """Determines the final sequence of actions to be triggered.

        Args:
            gateway_triggers: Each 'gateway_trigger' (ctx.triggered_id) provides the 'id' (or trigger_id) from the
                'actions_chain' that should be executed.

        Returns:
            List of final action sequence names which need to be triggered in order.

        Raises:
            PreventUpdate:
                If screen with triggers is rendered but component isn't triggered.
        """
        # Fetch all triggered action chain ids
        triggered_actions_chains_ids = [
            json.loads(triggered["prop_id"].split(".")[0])["trigger_id"] for triggered in ctx.triggered
        ]

        # Trigger only the on_page_load action if exists.
        # Otherwise, a single regular (non on_page_load) action is triggered
        actions_chain_to_trigger = next(
            (
                actions_chain_id
                for actions_chain_id in triggered_actions_chains_ids
                if ON_PAGE_LOAD_ACTION_PREFIX in actions_chain_id
            ),
            triggered_actions_chains_ids[0],
        )
        logger.debug("=========== ACTION ===============")
        logger.debug(f"Triggered component: {triggered_actions_chains_ids[0]}.")
        final_action_sequence = [
            {"Action ID": action.id, "Action name": action_functions[action.function._function]}
            for action in model_manager[actions_chain_to_trigger].actions  # type: ignore[attr-defined]
        ]
        logger.debug(f"Actions to be executed as part of the triggered ActionsChain: {final_action_sequence}")
        return [action_dict["Action ID"] for action_dict in final_action_sequence]

    # update remaining actions
    @callback(
        Output("remaining_actions", "data"),
        Input("cycle_breaker_div", "n_clicks"),
        Input("set_remaining", "data"),
        State("remaining_actions", "data"),
        prevent_initial_call=True,
    )
    def update_remaining_actions(
        action_finished: Optional[Dict[str, Any]],
        set_remaining: List[str],
        remaining_actions: List[str],
    ) -> List[str]:
        """Updates remaining action sequence that should be performed.

        Args:
            action_finished:
                Input that signalise action callback has finished
            set_remaining:
                Input that pass action sequence set in 'gateway' callback
            remaining_actions:
                State represents remaining actions sequence
        Returns:
            Initial or diminished list of remaining actions needed to be triggered.
        """
        # propagate sequence of actions from gateway callback
        triggered_id = ctx.triggered_id
        if triggered_id == "set_remaining":
            return set_remaining
        # pop first action
        if triggered_id == "cycle_breaker_div":
            return remaining_actions[1:]
        return []

    # executor
    @callback(
        *action_triggers,
        Input("remaining_actions", "data"),
        prevent_initial_call=True,
    )
    def executor(remaining_actions: List[str]) -> List[Any]:
        """Triggers callback of first action of remaining_actions list.

        Args:
            remaining_actions:
                Action sequence needed to be triggered.


        Returns:
            List of dash.no_update objects for all outputs except for next action.


        Raises:
            PreventUpdate:
                If there is no more remaining_actions needs to be triggered.
        """
        if not remaining_actions:
            raise PreventUpdate

        next_action = remaining_actions[0]
        output_list = ctx.outputs_list if isinstance(ctx.outputs_list, list) else [ctx.outputs_list]

        # return dash.no_update for all outputs except for next action
        trigger_next = [no_update if output["id"]["action_name"] != next_action else None for output in output_list]
        logger.debug(f"Starting execution of Action: {next_action}")
        return trigger_next

    # create action callbacks
    for action in actions:
        action._make_action_callback()

    # callback called after an action is finished
    @callback(
        Output("cycle_breaker_div", "children"),
        Input("action_finished", "data"),
        prevent_initial_call=True,
    )
    def after_action(*_) -> None:
        """Triggers clientside callback responsible for starting a new iteration."""
        logger.debug("Finished Action execution.")

    # callback that triggers the next iteration
    clientside_callback(
        """
        function(children) {
            document.getElementById("cycle_breaker_div").click()
            return children;
        }
        """,
        Output("cycle_breaker_empty_output_store", "data"),
        Input("cycle_breaker_div", "children"),
        prevent_initial_call=True,
    )
