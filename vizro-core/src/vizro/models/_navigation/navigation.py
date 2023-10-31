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
            Defaults to `None`.)
    """

    pages: Optional[NavPagesType] = None
    selector: Optional[NavSelectorType] = None

    # validators
    _validate_pages = validator("pages", allow_reuse=True, pre=True, always=True)(_validate_pages)

    @validator("selector", always=True)
    def set_selector(cls, selector, values):
        if selector is None:
            return Accordion(pages=values.get("pages"))

        if isinstance(selector, NavBar):
            if selector.pages is None and selector.items is None:
                selector.pages = values.get("pages")
                return selector
        return selector

    @_log_call
    def build(self, *, active_page_id=None):
        if isinstance(self.selector, NavBar):
            return self.selector.build(active_page_id=active_page_id)
        if isinstance(self.selector, Accordion):
            return html.Div(
                children=[
                    html.Div(className="hidden", id="nav_bar_outer"),
                    self.selector.build(active_page_id=active_page_id),
                ]
            )
