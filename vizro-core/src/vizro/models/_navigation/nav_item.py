from __future__ import annotations

import itertools
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import validator

from vizro._constants import STATIC_URL_PREFIX
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
    icon: Optional[str]
    pages: NavPagesType
    selector: Optional[Accordion] = None
    text: Optional[str] = ""
    max_text_length: int = 12  # check if that looks good

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @validator("selector", pre=True, always=True)
    def set_selector(cls, selector, values):
        if selector is None:
            return Accordion(pages=values.get("pages"))
        return selector

    @_log_call
    def build(self):
        return dbc.Button(  # add active argument for highlighting and check if needed , add active_page_id to build - similar to accordion
            id=self.id,
            children=[
                html.Img(
                    src=self.icon if self.icon else STATIC_URL_PREFIX + "/images/icon_1.svg",
                    className="nav-icon",
                ),
                self._create_icon_tooltip(),
            ],
            className="icon_button",
            href=self._get_page_href(),
        )

    def _get_page_href(self):
        if self.pages:
            first_page = (
                list(itertools.chain(*self.pages.values()))[0] if isinstance(self.pages, dict) else self.pages[0]
            )

            for page in dash.page_registry.values():
                if page["module"] == first_page:
                    return page["relative_path"]

    def _create_icon_tooltip(self):
        if self.tooltip:
            tooltip = dbc.Tooltip(
                children=html.P(self.tooltip),
                target=self.id,
                placement="bottom",
                className="custom_tooltip",
            )
            return tooltip
