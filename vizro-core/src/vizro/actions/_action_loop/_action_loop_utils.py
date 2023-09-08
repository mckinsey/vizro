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


def _get_actions(model: VizroBaseModel) -> List[ActionsChain]:
    """Gets the list of the ActionsChain models for any VizroBaseModel model."""
    if hasattr(model, "selector"):
        return model.selector.actions
    elif hasattr(model, "actions"):
        return model.actions
    return []


def _get_all_actions_chains_on_page(page: Page) -> List[ActionsChain]:
    """Gets the list of the ActionsChain models for the Page model."""
    return [
        actions_chain
        for page_item in chain([page], page.components, page.controls)
        for actions_chain in _get_actions(model=page_item)
    ]


def _get_actions_chains_on_registered_pages() -> List[ActionsChain]:
    """Gets list of ActionsChain models for registered pages."""
    actions_chains: List[ActionsChain] = []
    for registered_page in page_registry.values():
        try:
            page: Page = model_manager[registered_page["module"]]  # type: ignore[assignment]
        except KeyError:
            continue
        actions_chains.extend(_get_all_actions_chains_on_page(page=page))
    return actions_chains


def _get_actions_on_registered_pages() -> List[Action]:
    """Gets list of Action models for registered pages."""
    return [action for action_chain in _get_actions_chains_on_registered_pages() for action in action_chain.actions]
