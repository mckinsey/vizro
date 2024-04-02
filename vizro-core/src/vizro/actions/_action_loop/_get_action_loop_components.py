"""Contains utilities to create required components for the action loop."""

from dash import dcc, html

from vizro.actions._action_loop._action_loop_utils import (
    _get_actions_chains_on_all_pages,
    _get_actions_on_registered_pages,
)


def _get_action_loop_components() -> html.Div:
    """Gets all required components for the action loop.

    Returns
        List of dcc or html components.

    """
    actions_chains = _get_actions_chains_on_all_pages()
    actions = _get_actions_on_registered_pages()

    if not actions_chains:
        return html.Div(id="action_loop_components_div")

    # Fundamental components required for the smooth operation of the action loop mechanism.
    components = [
        dcc.Store(id="action_finished"),
        dcc.Store(id="remaining_actions", data=[]),
        html.Div(id="cycle_breaker_div", hidden=True),
        dcc.Store(id="cycle_breaker_empty_output_store"),
    ]

    # Additional component for every ActionChain in the system.
    # Represents a proxy component between visible UI component and the gateway of the action loop mechanism.
    # Required to avoid the "Unknown callback Input" issue for multiple page app examples.
    components.extend(
        [
            dcc.Store(
                id={"type": "gateway_input", "trigger_id": actions_chain.id},
                data=f"{actions_chain.id}",
            )
            for actions_chain in actions_chains
        ]
    )

    # Additional component for every Action in the system.
    # This component is injected as the only Input (trigger) inside each Action.
    # It enables that the action can be triggered only from the action loop mechanism.
    components.extend([dcc.Store(id={"type": "action_trigger", "action_name": action.id}) for action in actions])

    # Additional store with all action_triggers ids.
    components.append(dcc.Store(id="action_trigger_actions_id", data=[action.id for action in actions]))

    # Additional store that maps the actions chain trigger id and the list of action ids that should be executed.
    components.append(
        dcc.Store(
            id="trigger_to_actions_chain_mapper",
            data={
                actions_chain.id: [action.id for action in actions_chain.actions] for actions_chain in actions_chains
            },
        )
    )

    return html.Div(components, id="action_loop_components_div")
