from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, PrivateAttr, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models.types import NavigationPagesType

if TYPE_CHECKING:
    from vizro.models._navigation.accordion import Accordion


class Icon(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        title (Optional[str]): Title to be displayed in the tooltip on hover.
        icon_src (str): URI (relative or absolute) of the embeddable content.
        icon_href (Optional[str]): Existing page path to navigate to given page. Defaults to `None`.
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
                Defaults to `None`.
    """

    title: Optional[str]
    icon_src: str
    icon_href: Optional[str] = Field(None, description="Existing page path to navigate to given page.")
    pages: Optional[NavigationPagesType] = None
    _selector: Accordion = PrivateAttr()

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        self._set_selector()

    def _set_selector(self):
        from vizro.models._navigation.accordion import Accordion

        self._selector = Accordion(pages=self.pages)

    @_log_call
    def build(self):
        icon = dbc.Button(
            children=html.Img(
                src=self.icon_src,
                width=24,
                height=24,
                className="icon",
            ),
            className="icon_button",
            href=self.icon_href if bool(self.icon_href) else self._get_page_href(),
        )
        return icon

    def _get_page_href(self):
        if self.pages:
            first_page = next(iter(self.pages.values()))[0] if isinstance(self.pages, dict) else self.pages[0]

            for page in dash.page_registry.values():
                if page["module"] == first_page:
                    return page["relative_path"]
