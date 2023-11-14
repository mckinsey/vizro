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

    pages: Optional[NavPagesType] = None  # AM: yes but NavPagesType: note breaking change, maybe put whole type hint in
    selector: Optional[NavSelectorType] = None  # AM: yes

    # validators
    _validate_pages = validator("pages", allow_reuse=True, pre=True, always=True)(_validate_pages)

    @validator("selector", always=True)
    def set_selector(cls, selector, values):
        # AM: Will this check work correctly when pages not set?
        if "pages" not in values:
            return values

        selector = selector or Accordion()
        selector.pages = selector.pages or values["pages"]
        return selector

    @_log_call
    def build(self, *, active_page_id=None):
        selector = self.selector.build(active_page_id=active_page_id)
        if "nav_bar_outer" not in selector:
            # e.g. selector is Accordion and selector.build returns single html.Div with id="nav_panel_outer". This will
            # make it match the case e.g. selector is NavBar and selector.build returns html.Div containing children
            # with id="nav_bar_outer" and id="nav_panel_outer"
            selector = html.Div([html.Div(className="hidden", id="nav_bar_outer"), selector])

        return selector
