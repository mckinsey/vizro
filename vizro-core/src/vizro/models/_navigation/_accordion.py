import itertools
from collections.abc import Mapping
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, validator

from vizro._constants import ACCORDION_DEFAULT_TITLE
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages


class Accordion(VizroBaseModel):
    """Accordion to be used as selector in [`Navigation`][vizro.models.Navigation].

    Args:
        pages (Dict[str, List[str]]): A dictionary with a page group title as key and a list of page IDs as values.
    """

    pages: Dict[str, List[str]] = Field(
        ..., description="A dictionary with a page group title as key and a list of page IDs as values."
    )

    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @validator("pages", pre=True)
    def coerce_pages_type(cls, pages):
        if isinstance(pages, Mapping):
            return pages
        return {ACCORDION_DEFAULT_TITLE: pages}

    @_log_call
    def build(self, *, active_page_id=None):
        # Hide navigation panel if there is only one page
        if len(list(itertools.chain(*self.pages.values()))) == 1:
            return html.Div(hidden=True)

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
            id="nav_panel_outer",
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
