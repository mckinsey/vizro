from __future__ import annotations

import itertools
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType


class NavItem(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        tooltip (Optional[str]): Text to be displayed in the tooltip on icon hover.
        icon (Optional[str]): URI (relative or absolute) of the embeddable content.
        pages (NavPagesType): See [NavPagesType][vizro.models.types.NavPagesType].
    """

    tooltip: Optional[str]
    icon: str = "home"
    pages: NavPagesType
    selector: Optional[Accordion] = None
    text: Optional[str] = ""
    max_text_length: int = 9

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @validator("selector", pre=True, always=True)
    def set_selector(cls, selector, values):
        if selector is None:
            return Accordion(pages=values.get("pages"))
        return selector

    @_log_call
    def pre_build(self):
        if self.tooltip is None:
            if self.text and len(self.text) > self.max_text_length:
                self.tooltip = self.text
                self.text = self.text[:self.max_text_length]

    @_log_call
    def build(self, active_page_id):
        return dbc.Button(
            id=self.id,
            children=[
                html.Div(
                    children=[
                        html.Span(self.icon, className="material-symbols-outlined"),
                        html.Div(
                            children=[self.text],
                            className="icon-text",
                        )
                        if self.text
                        else html.Div(className="hidden"),
                    ],
                    className="nav-icon-text",
                ),
                self._create_icon_tooltip(),
            ],
            className="icon-button",
            href=dash.page_registry[self._get_first_page()]["relative_path"],
            active=self._get_first_page() == active_page_id,
        )

    def _create_icon_tooltip(self):
        if self.tooltip:
            tooltip = dbc.Tooltip(
                children=html.P(self.tooltip),
                target=self.id,
                placement="bottom",
                className="custom-tooltip",
            )
            return tooltip

    def _get_first_page(self):
        return list(itertools.chain(*self.pages.values()))[0] if isinstance(self.pages, dict) else self.pages[0]
