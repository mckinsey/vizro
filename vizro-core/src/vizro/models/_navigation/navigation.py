from __future__ import annotations

from dash import html

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

import dash_bootstrap_components as dbc

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType, _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType, NavSelectorType


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (NavPagesType): See [`NavPagesType`][vizro.models.types.NavPagesType]. Defaults to `[]`.
        nav_selector (NavSelectorType): See [`NavSelectorType`][vizro.models.types.NavSelectorType].
            Defaults to `None`.

    """

    pages: NavPagesType = []
    nav_selector: NavSelectorType = None

    # validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        # Since models instantiated in pre_build do not themselves have pre_build called on them, we call it manually
        # here. Note that not all nav_selectors have pre_build (Accordion does not).
        self.nav_selector = self.nav_selector or Accordion()
        self.nav_selector.pages = self.nav_selector.pages or self.pages
        if hasattr(self.nav_selector, "pre_build"):
            self.nav_selector.pre_build()

    @_log_call
    def build(self, *, active_page_id=None) -> _NavBuildType:
        nav_selector = self.nav_selector.build(active_page_id=active_page_id)

        if "nav-bar" not in nav_selector:
            # e.g. nav_selector is Accordion and nav_selector.build returns single html.Div with id="nav-panel".
            # This will make it match the case e.g. nav_selector is NavBar and nav_selector.build returns html.Div
            # containing children with id="nav-bar" and id="nav-panel"
            nav_selector = html.Div([dbc.Navbar(className="d-none invisible", id="nav-bar"), nav_selector])

        return nav_selector
