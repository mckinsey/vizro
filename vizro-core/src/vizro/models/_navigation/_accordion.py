from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import validator

from vizro._constants import ACCORDION_TITLE, MODULE_PAGE_404
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation.navigation import _validate_pages
from vizro.models.types import NavigationPagesType


class Accordion(VizroBaseModel):
    """Accordion to be used in Navigation Panel of Dashboard.

    Args:
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """

    pages: Optional[NavigationPagesType] = None

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def build(self):
        if self.pages:
            return self._create_accordion()
        return self._create_default_accordion()

    def _create_accordion_buttons(self, accordion_pages):
        return [
            dbc.Button(
                children=[page["name"]],
                key=page["relative_path"],
                className="accordion_button",
                href=page["relative_path"],
            )
            for page in dash.page_registry.values()
            for accordion_page in accordion_pages
            if accordion_page == page["module"] and page["module"] != MODULE_PAGE_404
        ]

    def _create_accordion_item(self, accordion_buttons, title=ACCORDION_TITLE):
        return dbc.AccordionItem(
            children=accordion_buttons,
            title=title.upper(),
            class_name="accordion_item",
        )

    def _create_default_accordion(self):
        accordion_buttons = [
            dbc.Button(
                children=[page["name"]],
                key=page["relative_path"],
                className="accordion_button",
                href=page["relative_path"],
            )
            for page in dash.page_registry.values()
            if page["module"] != MODULE_PAGE_404
        ]

        accordion_items = [self._create_accordion_item(accordion_buttons=accordion_buttons)]

        # Don't create accordion navigation if there is only one page and one accordion item
        if len(accordion_buttons) == len(accordion_items) == 1:
            return None

        return html.Div(
            children=dbc.Accordion(
                id=self.id,
                children=accordion_items,
                class_name="accordion",
                persistence=True,
                persistence_type="session",
            ),
            className="nav_panel",
            id=f"{self.id}_outer",
        )

    def _create_accordion(self):
        accordion_items = []

        if isinstance(self.pages, dict):
            for title, accordion_pages in self.pages.items():
                accordion_buttons = self._create_accordion_buttons(accordion_pages=accordion_pages)
                accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons, title=title))

        if isinstance(self.pages, list):
            accordion_buttons = self._create_accordion_buttons(accordion_pages=self.pages)
            accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons))

        if len(accordion_buttons) == len(accordion_items) == 1:
            return None

        return html.Div(
            children=dbc.Accordion(
                id=self.id,
                children=accordion_items,
                class_name="accordion",
                persistence=True,
                persistence_type="session",
            ),
            className="nav_panel",
            id=f"{self.id}_outer",
        )
