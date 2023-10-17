import itertools
from typing import Optional, Dict, List

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import validator

from vizro._constants import ACCORDION_DEFAULT_TITLE
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation.navigation import _validate_pages


class Accordion(VizroBaseModel):
    """Accordion to be used in Navigation Panel of Dashboard.

    Args:
        pages (Optional[NavigationPagesType]): See [`NavigationPagesType`][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """
    pages: Dict[str, List[str]]

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    # in validator:
    # if isinstance(self.pages, list):
    #     self.pages = {ACCORDION_DEFAULT_TITLE: self.pages}

    @_log_call
    def build(self, *, active_page_id=None):
        # assume for now that self.pages has at least one item.
        # Check if "not accordion_buttons" check also needed
        if len(list(itertools.chain(*self.pages.values()))) == 1:
            return html.Div(className="hidden")

        accordion_items = []

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

