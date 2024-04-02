"""Contains utilities to create required dash callbacks for the action loop."""

import logging
from typing import List

from dash import ClientsideFunction, Input, Output, State, clientside_callback

from vizro.actions._action_loop._action_loop_utils import (
    _get_actions_chains_on_all_pages,
    _get_actions_on_registered_pages,
)
from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID

logger = logging.getLogger(__name__)


def _build_action_loop_callbacks() -> None:
    """Creates all required dash callbacks for the action loop."""
    actions_chains = _get_actions_chains_on_all_pages()
    actions = _get_actions_on_registered_pages()

    if not actions_chains:
        return

    gateway_inputs: List[Input] = []
    for actions_chain in actions_chains:
        # Recalculating the trigger component id to use the underlying callable object as a trigger component if needed.
        actions_chain_trigger_component_id = actions_chain.trigger.component_id
        try:
            actions_chain_trigger_component = model_manager[ModelID(str(actions_chain_trigger_component_id))]
            # Use underlying callable object as a trigger component.
            if hasattr(actions_chain_trigger_component, "_input_component_id"):
                actions_chain_trigger_component_id = actions_chain_trigger_component._input_component_id
        # Not all action_chain_trigger_components are included in model_manager e.g. on_page_load_action_trigger
        except KeyError:
            pass

        # Callback that enables gateway callback to work in the multiple page app
        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="trigger_to_global_store"),
            Output({"type": "gateway_input", "trigger_id": actions_chain.id}, "data"),
            Input(
                component_id=actions_chain_trigger_component_id,
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

    # Determines the final sequence of actions to be triggered.
    clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="gateway"),
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
        ClientsideFunction(namespace="clientside", function_name="after_action_cycle_breaker"),
        Output("cycle_breaker_empty_output_store", "data"),
        Input("action_finished", "data"),
        prevent_initial_call=True,
    )
