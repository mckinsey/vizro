"""Contains utilities to extract the Action and ActionsChain models from registered pages only."""

from __future__ import annotations

from typing import TYPE_CHECKING, List
from vizro.managers import model_manager

if TYPE_CHECKING:
    from vizro.models import Action
    from vizro.models._action._actions_chain import ActionsChain


def _get_actions_chains_on_all_pages() -> List[ActionsChain]:
    """Gets list of ActionsChain models for registered pages."""
    from vizro.models import Page

    actions_chains: List[ActionsChain] = []
    for page_id, _ in model_manager._items_with_type(Page):
        actions_chains.extend(model_manager._get_page_actions_chains(page_id=page_id))
    return actions_chains


def _get_actions_on_registered_pages() -> List[Action]:
    """Gets list of Action models for registered pages."""
    return [action for action_chain in _get_actions_chains_on_all_pages() for action in action_chain.actions]
