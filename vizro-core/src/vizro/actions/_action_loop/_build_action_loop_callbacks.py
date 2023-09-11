"""Contains utilities to create required dash callbacks for the action loop."""
import json
import logging
from typing import Any, Dict, List, Optional

from dash import Input, Output, State, callback, clientside_callback, ctx, dcc, no_update
from dash.exceptions import PreventUpdate

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import action_functions
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

    if not actions_chains:
        return

    gateway_inputs: Dict[str, Any] = {
        "gateway_triggers": [],
        "cycle_breaker_div": Input("cycle_breaker_div", "n_clicks"),
        "remaining_actions": State("remaining_actions", "data"),

    }
    gateway_outputs: Dict[str, Any] = {
        "action_triggers": [Output({"type": "action_trigger", "action_name": action.id}, "data") for action in actions],
        "remaining_actions": Output("remaining_actions", "data"),
    }

    for actions_chain in actions_chains:
        # Callback that enables gateway callback to work in the multiple page app
        clientside_callback(
            """
            function(input, data) {
                return data;
            }
            """,
            Output({"type": "gateway_input", "trigger_id": actions_chain.id}, "data"),
            Input(
                component_id=actions_chain.trigger.component_id,
                component_property=actions_chain.trigger.component_property,
            ),
            State({"type": "gateway_input", "trigger_id": actions_chain.id}, "data"),
            prevent_initial_call=True,
        )

        gateway_inputs["gateway_triggers"].append(
            Input(
                component_id={"type": "gateway_input", "trigger_id": actions_chain.id},
                component_property="data",
            )
        )

    @callback(
        output=gateway_outputs,
        inputs=gateway_inputs,
        prevent_initial_call=True,
    )
    def gateway(**inputs: Dict[str, Any]):
        """GATEWAY."""
        remaining_actions = inputs["remaining_actions"]
        if ctx.triggered_id == "cycle_breaker_div":
            remaining_actions = remaining_actions[1:]
        else:
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
            remaining_actions = [action_dict["Action ID"] for action_dict in final_action_sequence]

        if not remaining_actions:
            raise PreventUpdate

        next_action = remaining_actions[0]
        output_list = ctx.outputs_grouping["action_triggers"]

        # Return dash.no_update for all outputs except for the next action
        trigger_next = [no_update if output["id"]["action_name"] != next_action else None for output in output_list]
        logger.debug(f"Starting execution of Action: {next_action}")

        return {
            "action_triggers": trigger_next,
            "remaining_actions": remaining_actions
        }

    # Callback that triggers the next iteration
    clientside_callback(
        """
        function(data) {
            document.getElementById("cycle_breaker_div").click()
            return [];
        }
        """,
        Output("cycle_breaker_empty_output_store", "data"),
        Input("action_finished", "data"),
        prevent_initial_call=True,
    )
