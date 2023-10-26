from __future__ import annotations

import itertools
from typing import List, Optional

from dash import html
from pydantic import validator

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation.nav_item import NavItem
from vizro.models.types import NavPagesType


class NavBar(VizroBaseModel):
    """Navigation bar to be used as a selector for `Navigation`.

    Args:
        pages (Optional[NavPagesType]): See [`NavPagesType`][vizro.models.types.NavPagesType].
            Defaults to `None`.
        items (List[NavItem]): List of NavItem models. Defaults to `[]`.
    """

    pages: Optional[NavPagesType] = None
    items: List[NavItem] = []

    @_log_call
    def pre_build(self):
        from vizro.models._navigation import Navigation

        _, navigation = next(model_manager._items_with_type(Navigation))

        if self.pages is None:
            self.pages = navigation.pages

        if not self.items:
            if isinstance(self.pages, list):
                self.items = [NavItem(pages=[page]) for page in self.pages]
            if isinstance(self.pages, dict):
                self.items = [NavItem(pages=value) for page, value in self.pages.items()]


    @_log_call
    def build(self, active_page_id):
        return html.Div(
            children=[
                html.Div(
                    children=[item.build(active_page_id=active_page_id) for item in self.items],
                    className="nav_bar",
                    id="nav_bar_outer",
                ),
                self._nav_panel_build(active_page_id=active_page_id),
            ]
        )

    def _nav_panel_build(self, active_page_id):
        for item in self.items:
            if isinstance(item.pages, list):
                if active_page_id in item.pages:
                    return item.selector.build(active_page_id=active_page_id)
            if isinstance(item.pages, dict):
                if active_page_id in list(itertools.chain(*item.pages.values())):
                    return item.selector.build(active_page_id=active_page_id)
