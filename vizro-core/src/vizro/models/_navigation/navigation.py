from __future__ import annotations

from typing import Annotated, Literal, cast

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType, _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType, NavSelectorType


class Navigation(VizroBaseModel):
    """Navigation to arrange hierarchy of [`Pages`][vizro.models.Page].

    Abstract: Usage documentation
        [How to customize the navigation](../user-guides/navigation.md)

    Args:
        pages (NavPagesType): See [`NavPagesType`][vizro.models.types.NavPagesType]. Defaults to `[]`.
        nav_selector (NavSelectorType | None): See [`NavSelectorType`][vizro.models.types.NavSelectorType].
            Defaults to `None`.

    """

    type: Literal["navigation"] = "navigation"
    pages: Annotated[
        NavPagesType,
        Field(default=[]),
    ]
    nav_selector: NavSelectorType | None = None

    @_log_call
    def pre_build(self):
        # TODO[MS]: Check validate pages properly
        self.pages = _validate_pages(self.pages)
        self.nav_selector = self.nav_selector or Accordion.from_pre_build(
            {"pages": self.pages},
            parent_model=self,
            field_name="nav_selector",
        )

    @_log_call
    def build(self, *, active_page_id=None) -> _NavBuildType:
        nav_selector = cast(NavSelectorType, self.nav_selector).build(active_page_id=active_page_id)

        if "nav-bar" not in nav_selector:
            # e.g. nav_selector is Accordion and nav_selector.build returns single html.Div with id="nav-panel".
            # This will make it match the case e.g. nav_selector is NavBar and nav_selector.build returns html.Div
            # containing children with id="nav-bar" and id="nav-panel"
            nav_selector = html.Div(children=[dbc.Navbar(id="nav-bar", className="d-none invisible"), nav_selector])

        return nav_selector
