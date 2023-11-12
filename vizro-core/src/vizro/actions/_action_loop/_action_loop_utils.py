"""Contains utilities to extract the Action and ActionsChain models from registered pages only."""

from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, List

from dash import page_registry

from vizro.managers import model_manager
from vizro.models import VizroBaseModel

if TYPE_CHECKING:
    from vizro.models import Action, Page
    from vizro.models._action._actions_chain import ActionsChain


def _get_actions_chains_on_registered_pages() -> List[ActionsChain]:
    """Gets list of ActionsChain models for registered pages."""
    actions_chains: List[ActionsChain] = []
    for registered_page in page_registry.values():
        try:
            page: Page = model_manager[registered_page["module"]]  # type: ignore[assignment]
        except KeyError:
            continue
        actions_chains.extend(page._get_page_actions_chains())
    return actions_chains


def _get_actions_on_registered_pages() -> List[Action]:
    """Gets list of Action models for registered pages."""
    return [action for action_chain in _get_actions_chains_on_registered_pages() for action in action_chain.actions]
