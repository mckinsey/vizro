from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import PrivateAttr, validator

from vizro._constants import STATIC_URL_PREFIX
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models.types import NavigationPagesType

if TYPE_CHECKING:
    from vizro.models._navigation.accordion import Accordion


class NavItem(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        tooltip (Optional[str]): Text to be displayed in the tooltip on icon hover.
        image (Optional[str]): URI (relative or absolute) of the embeddable content.
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
                Defaults to `None`.
    """

    tooltip: Optional[str]
    image: Optional[str]
    pages: Optional[NavigationPagesType] = None
    _selector: Accordion = PrivateAttr()

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        from vizro.models._navigation.accordion import Accordion

        self._selector = Accordion(pages=self.pages)

    @_log_call
    def build(self):
        return dbc.Button(
            id=self.id,
            children=[
                self._get_icon_image(),
                self._create_icon_tooltip(),
            ],
            className="icon_button",
            href=self._get_page_href(),
        )

    def _get_page_href(self):
        if self.pages:
            first_page = list(itertools.chain(*self.pages.values())) if isinstance(self.pages, dict) else self.pages[0]

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

    def _get_icon_image(self):
        image_path = self.image if self.image else STATIC_URL_PREFIX + "/images/icon_1.svg"

        return html.Img(
            src=image_path,
            width=24,
            height=24,
            className="icon",
        )
