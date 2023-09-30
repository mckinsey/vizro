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
            return self._create_custom_accordion()
        return self._create_default_accordion()

    def _create_accordion_buttons(self, accordion_pages):
        """Creates a button for each provided page."""
        # TODO: Better if we loop through pages from MM so the Accordion.build does not depend on app build.
        # However, this would require that only pages used in the Dashboard are registered in the MM.
        # Note: Relative path currently deviates from page.path for first page.
        return [
            dbc.Button(
                children=[page["name"]],
                key=page["relative_path"],
                className="accordion-item-button",
                href=page["relative_path"],
            )
            for page in dash.page_registry.values()
            if page["name"] in accordion_pages
        ]

    def _create_accordion_item(self, accordion_buttons, title=ACCORDION_TITLE):
        """Creates an accordion item for each sub-group of pages."""
        return dbc.AccordionItem(
            children=accordion_buttons,
            title=title.upper(),
            class_name="accordion_item",
        )

    def _get_accordion_container(self, accordion_items, accordion_buttons):
        # Don't create accordion container if there is only one page and one accordion item
        if len(accordion_buttons) == len(accordion_items) == 1:
            return None

        return html.Div(
            children=[
                dbc.Accordion(
                    id=self.id,
                    children=accordion_items,
                    class_name="accordion",
                    persistence=True,
                    persistence_type="session",
                ),
                html.Div(className="keyline"),
            ],
            className="nav_panel",
            id=f"{self.id}_outer",
        )

    def _create_default_accordion(self):
        """Creates a default accordion with all pages provided to the Dashboard."""
        registered_pages = [page for page in dash.page_registry.keys() if page != MODULE_PAGE_404]
        accordion_buttons = self._create_accordion_buttons(accordion_pages=registered_pages)
        accordion_items = [self._create_accordion_item(accordion_buttons=accordion_buttons)]
        return self._get_accordion_container(accordion_items=accordion_items, accordion_buttons=accordion_buttons)

    def _create_custom_accordion(self):
        """Creates a custom accordion only with user-provided pages."""
        accordion_items = []
        if isinstance(self.pages, dict):
            for title, accordion_pages in self.pages.items():
                accordion_buttons = self._create_accordion_buttons(accordion_pages=accordion_pages)
                accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons, title=title))

        if isinstance(self.pages, list):
            accordion_buttons = self._create_accordion_buttons(accordion_pages=self.pages)
            accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons))
        return self._get_accordion_container(accordion_items=accordion_items, accordion_buttons=accordion_buttons)
