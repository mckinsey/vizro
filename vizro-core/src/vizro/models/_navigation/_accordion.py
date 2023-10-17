import itertools
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
        accordion_items = []

        # self.pages = {"section 1": ["Page 1", "Page 2"], "section 2": ["Page 3"]}

        # self.pages = ["Page 1", "Page 2"]  -> ACCORDION_DEFAULT_TITLE
        if isinstance(self.pages, list):
            self.pages = {ACCORDION_DEFAULT_TITLE: self.pages}
        # Turn into top case either here or in validator.

        # assume for now that self.pages has at least one item.
        # Check if "not accordion_buttons" check also needed
        if len(list(itertools.chain(*self.pages.values()))) == 1:
            return html.Div(className="hidden")

        for page_group, page_members in self.pages.items():
            accordion_buttons = self._create_accordion_buttons(pages=page_members, active_page_id=active_page_id)
            accordion_items.append(
                dbc.AccordionItem(
                    children=accordion_buttons,
                    title=page_group.upper(),
                    class_name="accordion_item",
                )
            )

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

