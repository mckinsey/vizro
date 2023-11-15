from __future__ import annotations

from typing import Optional

from dash import html
from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models._navigation.nav_bar import NavBar
from vizro.models.types import NavPagesType, NavSelectorType


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavPagesType]): See [`NavPagesType`][vizro.models.types.NavPagesType].
            Defaults to `None`.
        selector (Optional[NavSelectorType]): See [`NavSelectorType`][vizro.models.types.NavSelectorType].
            Defaults to `None`.
    """

    pages: NavPagesType = []  # AM: yes but NavPagesType: note breaking change, maybe put whole type hint in
    selector: NavSelectorType = Accordion()

    # validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        # Since models instantiated in pre_build do not themselves have pre_build called on them, we call it manually
        # here. Note that not all selectors have pre_build (Accordion does not).
        self.selector.pages = self.selector.pages or self.pages
        if hasattr(self.selector, "pre_build"):
            self.selector.pre_build()

    @_log_call
    def build(self, *, active_page_id=None):
        selector = self.selector.build(active_page_id=active_page_id)
        if "nav_bar_outer" not in selector:
            # e.g. selector is Accordion and selector.build returns single html.Div with id="nav_panel_outer". This will
            # make it match the case e.g. selector is NavBar and selector.build returns html.Div containing children
            # with id="nav_bar_outer" and id="nav_panel_outer"
            selector = html.Div([html.Div(className="hidden", id="nav_bar_outer"), selector])

        return selector
