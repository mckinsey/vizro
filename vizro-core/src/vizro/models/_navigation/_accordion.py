from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import validator

from vizro._constants import ACCORDION_DEFAULT_TITLE
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
        return self._create_accordion()

    def _create_accordion_buttons(self, pages):
        """Creates a button for each provided page."""
        # TODO: Better if we loop through pages from MM so the Accordion.build does not depend on dashboard build.
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
            if page["name"] in pages
        ]

    def _create_accordion_item(self, accordion_buttons, title=ACCORDION_DEFAULT_TITLE):
        """Creates an accordion item for each sub-group of pages."""
        return dbc.AccordionItem(
            children=accordion_buttons,
            title=title.upper(),
            class_name="accordion_item",
        )

    def _get_accordion_container(self, accordion_items, accordion_buttons):
        # Return no container if there is only one page in the dashboard
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

    def _create_accordion(self):
        """Creates a custom accordion only with user-provided pages."""
        accordion_items = []
        if isinstance(self.pages, dict):
            for page_group, page_members in self.pages.items():
                accordion_buttons = self._create_accordion_buttons(pages=page_members)
                accordion_items.append(
                    self._create_accordion_item(accordion_buttons=accordion_buttons, title=page_group)
                )

        if isinstance(self.pages, list):
            accordion_buttons = self._create_accordion_buttons(pages=self.pages)
            accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons))
        return self._get_accordion_container(accordion_items=accordion_items, accordion_buttons=accordion_buttons)
