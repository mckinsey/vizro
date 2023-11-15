from __future__ import annotations
from collections.abc import Mapping

import itertools
from typing import List, Optional, cast, Literal, Dict

from dash import html
from pydantic import validator, Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.nav_item import NavItem


class NavBar(VizroBaseModel):
    """Navigation bar to be used as a selector for `Navigation`.

    Args:
        type (Literal["navbar"]): Defaults to `"navbar"`.
        pages (Optional[Dict[str, List[str]]]): A dictionary with a page group title as key and a list of page IDs as
            values.
        items (Optional[List[NavItem]]): See [`NavItem`][vizro.models.NavItem]. Defaults to `[]`.
    """

    type: Literal["navbar"] = "navbar"  # AM: nav_bar?
    pages: Optional[Dict[str, List[str]]] = Field(
        {}, description="A dictionary with a page group title as key and a list of page IDs as values."
    )
    items: Optional[List[NavItem]] = []  # AM: think about name

    # validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @validator("pages", pre=True)
    def coerce_pages_type(cls, pages):
        if isinstance(pages, Mapping):
            return pages
        return {page: [page] for page in pages}

    @_log_call
    def pre_build(self):
        self.items = self.items or [NavItem(text=group_title, pages=pages) for group_title, pages in self.pages.items()]

        for position, item in enumerate(self.items, 1):
            item.icon = item.icon or f"filter_{position}" if position <= 9 else "filter_9+"

        # Since models instantiated in pre_build do not themselves have pre_build called on them, we call it manually
        # here.
        for item in self.items:
            item.pre_build()

        return self.items

    @_log_call
    def build(self, *, active_page_id=None):
        # We always show all the navitem buttons, but only show the accordion for the active page. This works because
        # item.build only returns the nav_panel_outer Div when the item is active.
        # In future maybe we should do this by showing all navigation panels and then setting hidden=True for all but
        # one using a clientside callback?
        # Wrapping built_items into html.Div here is not for rendering purposes but so that we can look up the
        # components by id easily instead of needing to iterate through a nested list.
        built_items = html.Div([item.build(active_page_id=active_page_id) for item in self.items])
        buttons = [built_items[item.id] for item in self.items]
        if "nav_panel_outer" in built_items:
            nav_panel_outer = built_items["nav_panel_outer"]
        else:
            # Active page is not in navigation at all, so hide navigation panel.
            nav_panel_outer = html.Div(hidden=True, id="nav_panel_outer")

        return html.Div([html.Div(buttons, className="nav-bar", id="nav_bar_outer"), nav_panel_outer])
