"""Contains utilities to create required dash callbacks for the action loop."""
import logging
from typing import List

from dash import Input, Output, State, clientside_callback

from vizro.actions._action_loop._action_loop_utils import (
    _get_actions_chains_on_registered_pages,
    _get_actions_on_registered_pages,
)

logger = logging.getLogger(__name__)


def _build_action_loop_callbacks() -> None:
    """Creates all required dash callbacks for the action loop."""
    actions_chains = _get_actions_chains_on_registered_pages()
    actions = _get_actions_on_registered_pages()

    if not actions_chains:
        return

    gateway_inputs: List[Input] = []
    for actions_chain in actions_chains:
        # Callback that enables gateway callback to work in the multiple page app
        clientside_callback(
            """
            function trigger_to_global_store(input, data) {
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

        gateway_inputs.append(
            Input(
                component_id={"type": "gateway_input", "trigger_id": actions_chain.id},
                component_property="data",
            )
        )

    clientside_callback(
        """
        function gateway(
            remaining_actions,
            trigger_to_actions_chain_mapper,
            action_trigger_actions_id,
            cycle_breaker_div,
            ...gateway_triggers)
        {
            // Based on the triggered input, determines what is the next action to execute.
            var ctx_triggered, triggered_actions_chains_ids, actions_chain_to_trigger, next_action, trigger_next;

            ctx_triggered = dash_clientside.callback_context.triggered

            // If the 'cycle_breaker_div' is triggered that means that at least one action is already executed.
            if (ctx_triggered.length == 1 && ctx_triggered[0]['prop_id'].split('.')[0] === 'cycle_breaker_div') {
                // If there's no more actions to execute, stop the loop perform.
                if (remaining_actions.length == 0) {
                    return dash_clientside.PreventUpdate
                }
            }
            // Actions chain is triggered from the UI, find the list of actions that should be executed.
            else {
                triggered_actions_chains_ids = []
                for (let i = 0; i < ctx_triggered.length; i++) {
                    triggered_actions_chains_ids.push(JSON.parse(ctx_triggered[i]['prop_id'].split('.')[0])['trigger_id']);
                }

                // Trigger only the on_page_load action if exists.
                // Otherwise, a single regular (non on_page_load) actions chain is triggered.
                function findStringInList(list, string) {
                    for (let i = 0; i < list.length; i++) {
                        if (list[i].indexOf(string) !== -1) {
                            // The on_page_load action found
                            return list[i];
                        }
                    }
                    // A single regular (non on_page_load) action is triggered.
                    return list[0];
                }
                actions_chain_to_trigger = findStringInList(triggered_actions_chains_ids, "on_page_load");
                remaining_actions = trigger_to_actions_chain_mapper[actions_chain_to_trigger];
            }

            next_action = remaining_actions[0]

            // Return dash.no_update for all outputs except for the next action
            trigger_next = []
            for (let i = 0; i < action_trigger_actions_id.length; i++) {
                if (next_action === action_trigger_actions_id[i]) {
                    trigger_next.push(null)
                }
                else {
                    trigger_next.push(dash_clientside.no_update)
                }
            }

            return [remaining_actions.slice(1)].concat(trigger_next)
        }
        """,
        output=[Output("remaining_actions", "data")]
        + [Output({"type": "action_trigger", "action_name": action.id}, "data") for action in actions],
        inputs=[
            State("remaining_actions", "data"),
            State("trigger_to_actions_chain_mapper", "data"),
            State("action_trigger_actions_id", "data"),
            Input("cycle_breaker_div", "n_clicks"),
            *gateway_inputs,
        ],
        prevent_initial_call=True,
    )

    # Callback that triggers the next iteration
    clientside_callback(
        """
        function after_action_cycle_breaker(data) {
            document.getElementById("cycle_breaker_div").click()
            return [];
        }
        """,
        Output("cycle_breaker_empty_output_store", "data"),
        Input("action_finished", "data"),
        prevent_initial_call=True,
    )
