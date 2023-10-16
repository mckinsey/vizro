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
        pages (Optional[NavigationPagesType]): See [`NavigationPagesType`][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """

    # I went for Li's idea of being strict about e.g. NavigationDropdown taking only a flat list and Accordion only
    # taking a grouped dictionary. We can change this if it seems to make things more confusing though and just e.g.
    # convert a pages dictionary inside NavigationDropdown to flatten it to just take the values.
    # pages: Optional[Dict[str, List[str]]]
    # currently accepts List[str] too
    # don't want to get all pages here.
    # Make it non-optional for now anyway. Doesn't make sense as optional given now don't have Dropdown etc.
    # And there's only one field here anyway.
    # (technically breaking if it was public)
    pages: Optional[NavigationPagesType] = None
    # 2 cases: list of pages, dictionary of pages
    # Convert both in validator to dict.

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def build(self, *, active_page_id=None):
        # Could now be None in return - probably not good. Traces through to page._arrange_containers
        # Remember union types awkward and lead to bugs, especially None type
        return self._create_accordion(active_page_id=active_page_id)

    def _create_accordion_buttons(self, pages, active_page_id):
        """Creates a button for each provided page that is registered."""
        accordion_buttons = []
        for page_id in pages:
            try:
                page = dash.page_registry[page_id]
            except KeyError as exc:
                raise KeyError(
                    f"Page with ID {page_id} cannot be found. Please add the page to `Dashboard.pages`"
                ) from exc
            accordion_buttons.append(
                dbc.Button(
                    children=[page["name"]],
                    key=page["relative_path"],
                    className="accordion-item-button",
                    active=page_id == active_page_id,
                    href=page["relative_path"],
                )
            )
        return accordion_buttons

    def _create_accordion_item(self, accordion_buttons, title=ACCORDION_DEFAULT_TITLE):
        # Defaulting behaviour in wrong place here as makes code in _create_accordion different
        """Creates an accordion item for each sub-group of pages."""
        return dbc.AccordionItem(
            children=accordion_buttons,
            title=title.upper(),
            class_name="accordion_item",
        )

    def _get_accordion_container(self, accordion_items, accordion_buttons):
        # Return no container if there is only one page in the dashboard or no pages exist
        # Only need accordion_buttons for this one line -> good sign not needed really or should go elsewhere
        # Do earlier on in flow so don't need to computer accordion_buttons etc. in this case.
        if (len(accordion_buttons) == len(accordion_items) == 1) or not accordion_buttons:
            return None

        return html.Div(
            children=[
                dbc.Accordion(
                    id=self.id,
                    children=accordion_items,
                    class_name="accordion",
                    persistence=True,
                    persistence_type="session",
                    always_open=True,
                ),
                html.Hr(),
            ],
            className="nav_panel",
            id=f"{self.id}_outer",
        )

    def _create_accordion(self, active_page_id):
        """Creates a custom accordion only with user-provided pages."""
        accordion_items = []
        if isinstance(self.pages, dict):
            for page_group, page_members in self.pages.items():
                accordion_buttons = self._create_accordion_buttons(pages=page_members, active_page_id=active_page_id)
                accordion_items.append(
                    self._create_accordion_item(accordion_buttons=accordion_buttons, title=page_group)
                )

        if isinstance(self.pages, list):
            # Turn into top case either here or in validator.
            # GENERAL RULE: do conversion early so don't need to handle different cases.
            accordion_buttons = self._create_accordion_buttons(pages=self.pages, active_page_id=active_page_id)
            accordion_items.append(self._create_accordion_item(accordion_buttons=accordion_buttons))
        return self._get_accordion_container(accordion_items=accordion_items, accordion_buttons=accordion_buttons)
