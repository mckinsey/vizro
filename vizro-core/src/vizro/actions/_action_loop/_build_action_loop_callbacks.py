"""Contains utilities to create required dash callbacks for the action loop."""
import json
import logging
from typing import Any, Dict, List, Optional

from dash import Input, Output, State, callback, clientside_callback, ctx, dcc, no_update
from dash.exceptions import PreventUpdate

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions._action_loop._action_loop_utils import (
    _get_actions_chains_on_registered_pages,
    _get_actions_on_registered_pages,
)
from vizro.managers import model_manager

logger = logging.getLogger(__name__)


def _build_action_loop_callbacks() -> None:
    """Creates all required dash callbacks for the action loop."""
    # TODO - Reduce the number of the callbacks in the action loop mechanism
    actions_chains = _get_actions_chains_on_registered_pages()
    actions = _get_actions_on_registered_pages()

    gateway_triggers: List[Input] = []
    for actions_chain in actions_chains:
        # TODO: Potentially convert to clientside callback
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
            {"Action ID": action.id, "Action name": action.function._function.__name__}
            for action in model_manager[actions_chain_to_trigger].actions  # type: ignore[attr-defined]
        ]

        logger.debug(f"Actions to be executed as part of the triggered ActionsChain: {final_action_sequence}")
        return [action_dict["Action ID"] for action_dict in final_action_sequence]

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
        # Propagate sequence of actions from gateway callback
        triggered_id = ctx.triggered_id
        if triggered_id == "set_remaining":
            return set_remaining
        # Pop first action
        if triggered_id == "cycle_breaker_div":
            return remaining_actions[1:]
        return []

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

        # Return dash.no_update for all outputs except for the next action
        trigger_next = [no_update if output["id"]["action_name"] != next_action else None for output in output_list]
        logger.debug(f"Starting execution of Action: {next_action}")
        return trigger_next

    # Callback called after an action is finished
    @callback(
        Output("cycle_breaker_div", "children"),
        Input("action_finished", "data"),
        prevent_initial_call=True,
    )
    def after_action(*_) -> None:
        """Triggers clientside callback responsible for starting a new iteration."""
        logger.debug("Finished Action execution.")

    # Callback that triggers the next iteration
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
