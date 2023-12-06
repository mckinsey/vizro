from __future__ import annotations

from collections.abc import Mapping
from typing import Dict, List, Literal

from dash import html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType, _validate_pages
from vizro.models._navigation.nav_link import NavLink


class NavBar(VizroBaseModel):
    """Navigation bar to be used as a nav_selector for `Navigation`.

    Args:
        type (Literal["nav_bar"]): Defaults to `"nav_bar"`.
        pages (Dict[str, List[str]]): Mapping from name of a pages group to a list of page IDs. Defaults to `{}`.
        items (List[NavLink]): See [`NavLink`][vizro.models.NavLink]. Defaults to `[]`.
    """

    type: Literal["nav_bar"] = "nav_bar"
    pages: Dict[str, List[str]] = Field({}, description="Mapping from name of a pages group to a list of page IDs.")
    items: List[NavLink] = []

    # validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @validator("pages", pre=True)
    def coerce_pages_type(cls, pages):
        if isinstance(pages, Mapping):
            return pages
        return {page: [page] for page in pages}

    @_log_call
    def pre_build(self):
        self.items = self.items or [
            NavLink(label=group_title, pages=pages) for group_title, pages in self.pages.items()
        ]

        for position, item in enumerate(self.items, 1):
            # The filter icons are named filter_1, filter_2, etc. up to filter_9. If there are more than 9 items, then
            # the 10th and all subsequent items are named filter_9+.
            item.icon = item.icon or f"filter_{position}" if position <= 9 else "filter_9+"  # noqa: PLR2004

        # Since models instantiated in pre_build do not themselves have pre_build called on them, we call it manually
        # here.
        for item in self.items:
            item.pre_build()

        return self.items

    @_log_call
    def build(self, *, active_page_id=None) -> _NavBuildType:
        # We always show all the nav_link buttons, but only show the accordion for the active page. This works because
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
