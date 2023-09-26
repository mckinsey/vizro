from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional, Union, List, Dict, Any

from pydantic import PrivateAttr, validator
from dash import dcc, html

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import NavigationPagesType
from vizro.models._navigation.icon import Icon


class NavBar(VizroBaseModel):
    pages: Optional[Union[List[str], Dict[str, List[str]]]]
    items: Optional[List[Icon]]

    @_log_call
    def pre_build(self):
        if self.items is None:
            if isinstance(self.pages, list):
                self.items = [Icon(pages=page) for page in self.pages]
            if isinstance(self.pages, dict):
                self.items = [Icon(pages=value) for page, value in self.pages.values()]

    @_log_call
    def build(self, page_id):
        if self.items:
            items = [item.build() for item in self.items]
            nav_bar = html.Div(
                children=items,
                className="nav_bar",
            )
            nav_panel = self._nav_panel_build(page_id=page_id)

            return nav_bar, nav_panel

    def _nav_panel_build(self, page_id):
        for item in self.items:
            if isinstance(item.pages, list):
                if page_id in item.pages:
                    return item.selector.build()

            if isinstance(item.pages, dict):
                pages = []
                for row in item.pages.values():
                    pages.extend(row)
                if page_id in pages:
                    return item.selector.build()
