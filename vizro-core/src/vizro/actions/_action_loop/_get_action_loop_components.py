"""Contains utilities to create required components for the action loop."""
from typing import List, Union

from dash import dcc, html

from vizro.actions._action_loop._action_loop_utils import (
    _get_actions_chains_on_registered_pages,
    _get_actions_on_registered_pages,
)


# TODO - Return only components for selected dashboard pages (not for all)
def _get_action_loop_components() -> List[Union[dcc.Store, html.Div]]:
    """Gets all required components for the action loop.

    Returns:
        List of dcc or html components.
    """
    actions_chains = _get_actions_chains_on_registered_pages()
    actions = _get_actions_on_registered_pages()

    # Fundamental components required for the smooth operation of the loop mechanism.
    components = [
        dcc.Store(id="empty_input_store"),
        dcc.Store(id="empty_output_store"),
        dcc.Store(id="action_finished"),
        dcc.Store(id="set_remaining"),
        dcc.Store(id="remaining_actions"),
        html.Div(id="cycle_breaker_div", style={"display": "hidden"}),
        dcc.Store(id="cycle_breaker_empty_output_store"),
    ]

    # Additional component for every ActionChain in the system
    components.extend(
        [
            dcc.Store(
                id={"type": "gateway_input", "trigger_id": actions_chain.id},
                data=f"{actions_chain.id}",
            )
            for actions_chain in actions_chains
        ]
    )

    # Additional component for every Action in the system
    components.extend([dcc.Store(id={"type": "action_trigger", "action_name": action.id}) for action in actions])

    return components
