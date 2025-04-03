from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Literal, Union

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType, _validate_pages
from vizro.models._navigation.nav_link import NavLink
from vizro.models.types import ModelID


def coerce_pages_type(pages: Union[list[str], dict[str, list[str]]]) -> dict[str, list[str]]:
    if isinstance(pages, Mapping):
        return pages
    return {page: [page] for page in pages}


class NavBar(VizroBaseModel):
    """Navigation bar to be used as a nav_selector for `Navigation`.

    Args:
        type (Literal["nav_bar"]): Defaults to `"nav_bar"`.
        pages (dict[str, list[ModelID]]): Mapping from name of a pages group to a list of page IDs. Defaults to `{}`.
        items (list[NavLink]): See [`NavLink`][vizro.models.NavLink]. Defaults to `[]`.

    """

    type: Literal["nav_bar"] = "nav_bar"
    pages: Annotated[
        dict[str, list[ModelID]],
        AfterValidator(_validate_pages),
        BeforeValidator(coerce_pages_type),
        Field(default={}, description="Mapping from name of a pages group to a list of page IDs."),
    ]
    items: list[NavLink] = []

    @_log_call
    def pre_build(self):
        self.items = self.items or [
            NavLink(label=group_title, pages=pages) for group_title, pages in self.pages.items()
        ]

        for position, item in enumerate(self.items, 1):
            # The default icons are named filter_1, filter_2, etc. up to filter_9.
            # If there are more than 9 items, then the 10th and all subsequent items are named filter_9+.
            icon_default = f"filter_{position}" if position <= 9 else "filter_9+"  # noqa: PLR2004
            item.icon = item.icon or icon_default

        # Since models instantiated in pre_build do not themselves have pre_build called on them, we call it manually
        # here.
        for item in self.items:
            item.pre_build()

        return self.items

    @_log_call
    def build(self, *, active_page_id=None) -> _NavBuildType:
        # We always show all the nav_links, but only show the accordion for the active page. This works because
        # item.build only returns the nav_panel Div when the item is active.
        # In future maybe we should do this by showing all navigation panels and then setting hidden=True for all but
        # one using a clientside callback?
        # Wrapping built_items into html.Div here is not for rendering purposes but so that we can look up the
        # components by id easily instead of needing to iterate through a nested list.
        built_items = html.Div([item.build(active_page_id=active_page_id) for item in self.items])
        nav_links = [built_items[item.id] for item in self.items]
        if "nav-panel" in built_items:
            nav_panel = built_items["nav-panel"]
        else:
            # Active page is not in navigation at all, so hide navigation panel.
            nav_panel = dbc.Nav(id="nav-panel", className="d-none invisible")

        # `flex-column` ensures that we return a vertical NavBar. In the future, we could use that className
        # to create a horizontal NavBar.
        return html.Div(children=[dbc.Navbar(id="nav-bar", children=nav_links, className="flex-column"), nav_panel])
