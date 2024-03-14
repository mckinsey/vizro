"""Contains utilities to extract the Action and ActionsChain models from registered pages only."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import dash

from vizro.managers import model_manager
from vizro.managers._model_manager import ModelID

if TYPE_CHECKING:
    from vizro.models import Action, Page
    from vizro.models._action._actions_chain import ActionsChain


def _get_actions_chains_on_all_pages() -> List[ActionsChain]:
    """Gets list of ActionsChain models for registered pages."""
    actions_chains: List[ActionsChain] = []
    # TODO: once dash.page_registry matches up with model_manager, change this to use purely model_manager.
    # Making the change now leads to problems since there can be Action models defined that aren't used in the
    # dashboard.
    # See https://github.com/mckinsey/vizro/pull/366.
    for registered_page in dash.page_registry.values():
        try:
            page: Page = model_manager[registered_page["module"]]
        except KeyError:
            continue
        actions_chains.extend(model_manager._get_page_actions_chains(page_id=ModelID(str(page.id))))
    return actions_chains


def _get_actions_on_registered_pages() -> List[Action]:
    """Gets list of Action models for registered pages."""
    return [action for action_chain in _get_actions_chains_on_all_pages() for action in action_chain.actions]
