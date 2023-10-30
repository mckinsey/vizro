from __future__ import annotations

import itertools
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, root_validator, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType


class NavItem(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        pages (NavPagesType): See [NavPagesType][vizro.models.types.NavPagesType].
        icon (str): URI (relative or absolute) of the embeddable content. Defaults to "home".
        max_text_length (int): Character limit for `text` argument. Defaults to 8.
        text (Optional[str]): Text to be displayed below the icon. Defaults to `None`.
        tooltip (Optional[str]): Text to be displayed in the icon tooltip on hover.
        selector (Optional[Accordion]): See [`Accordion`][vizro.models.Accordion]. Defaults to `None`.
    """

    pages: NavPagesType
    icon: str = Field("home", description="URI (relative or absolute) of the embeddable content.")
    max_text_length: int = Field(8, description="Character limit for `text` argument.")
    text: Optional[str] = Field(None, description="Text to be displayed below the icon.")
    tooltip: Optional[str] = Field(None, description="Text to be displayed in the icon tooltip on hover.")
    selector: Optional[Accordion] = None

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @validator("selector", pre=True, always=True)
    def set_selector(cls, selector, values):
        if selector is None:
            return Accordion(pages=values.get("pages"))
        return selector

    @root_validator()
    def set_text_and_tooltip(cls, values):
        if values["text"] and (len(values["text"]) > values["max_text_length"]):
            if values["tooltip"] is None:
                values["tooltip"] = values["text"]
            values["text"] = values["text"][: values["max_text_length"]]
        return values

    @_log_call
    def build(self, active_page_id):
        icon_first_page = (
            list(itertools.chain(*self.pages.values()))[0] if isinstance(self.pages, dict) else self.pages[0]
        )
        icon_div = (
            html.Span(self.icon, className="material-symbols-outlined") if self.icon else html.Div(className="hidden")
        )
        text_div = html.Div(children=[self.text], className="icon-text") if self.text else html.Div(className="hidden")

        return dbc.Button(
            id=self.id,
            children=[
                html.Div(
                    children=[
                        icon_div,
                        text_div,
                    ],
                    className="nav-icon-text",
                ),
                self._create_icon_tooltip(),
            ],
            className="icon-button",
            href=dash.page_registry[icon_first_page]["relative_path"],
            active=icon_first_page == active_page_id,
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
