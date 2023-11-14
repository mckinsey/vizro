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
    # pages: Optional[NavPagesType] = None
    pages: Optional[Dict[str, List[str]]] = Field(
        {}, description="A dictionary with a page group title as key and a list of page IDs as values."
    )
    items: Optional[List[NavItem]] = []  # AM: think about name

    # validators
    _validate_pages = validator("pages", allow_reuse=True, pre=True, always=True)(_validate_pages)

    @validator("pages", pre=True)
    def coerce_pages_type(cls, pages):
        if isinstance(pages, Mapping):
            return pages
        return {page: [page] for page in pages}

    @validator("items", always=True)
    def set_items(cls, items, values):
        # AM: Will this check work correctly when pages not set?
        if "pages" not in values:
            return values

        items = items or [NavItem(text=group_title, pages=pages) for group_title, pages in values["pages"].items()]

        # AM: test works if set some icons but not others
        for position, item in enumerate(items):
            # There are only 6 looks icons. If there are more than 6 items, the icons will repeat.
            item.icon = item.icon or f"looks_{position % 6 + 1}"

        return items

    @_log_call
    def build(self, *, active_page_id=None):
        # We always show all the navitem buttons, but only show the accordion for the active page. This works because
        # item.build only returns the nav_panel_outer Div when the item is active.
        # In future maybe we should do this by showing all navigation panels and then setting hidden=True for all but
        # one using a clientside callback?
        built_items = [item.build() for item in self.items]
        buttons = [item[item.id] for item in built_items]
        if "nav_panel_outer" in built_items:
            nav_panel_outer = built_items["nav_panel_outer"]
        else:
            # Active page is not in navigation, so hide navigation panel.
            nav_panel_outer = html.Div(hidden=True, id="nav_panel_outer")

        return html.Div([html.Div(buttons, className="nav-bar", id="nav_bar_outer"), nav_panel_outer])
