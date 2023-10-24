from __future__ import annotations

from typing import List, Optional

from dash import html
from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation.nav_item import NavItem
from vizro.models.types import NavPagesType


class NavBar(VizroBaseModel):
    """Navigation bar to be used as a selector for `Navigation`.

    Args:
        pages (Optional[NavPagesType]): See [`NavPagesType`][vizro.models.types.NavPagesType].
            Defaults to `None`.
        items (List[NavItem]): List of NavItem models. Defaults to `None`.
    """

    pages: Optional[NavPagesType] = None
    items: Optional[List[NavItem]] = None

    @validator("items", always=True)
    def _validate_items(cls, items, values):
        if items is not None and not items:
            raise ValueError("Ensure this value has at least 1 item.")

        if not items:
            if isinstance(values.get("pages"), list):
                return [NavItem(pages=[page]) for page in values.get("pages")]
            if isinstance(values.get("pages"), dict):
                return [NavItem(pages=value) for page, value in values.get("pages").items()]
        return items

    @_log_call
    def build(self, active_page_id):
        return html.Div(
            children=[
                html.Div(children=[item.build() for item in self.items], className="nav_bar", id="nav_bar_outer"),
                self._nav_panel_build(active_page_id=active_page_id),
            ]
        )

    def _nav_panel_build(self, active_page_id):
        if self.items:
            for item in self.items:
                if isinstance(item.pages, list):
                    if active_page_id in item.pages:
                        return item.selector.build(active_page_id=active_page_id)
                if isinstance(item.pages, dict):
                    pages = [page for row in item.pages.values() for page in row]
                    if active_page_id in pages:
                        return item.selector.build(active_page_id=active_page_id)
