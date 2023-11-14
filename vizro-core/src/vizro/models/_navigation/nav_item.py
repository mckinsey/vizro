from __future__ import annotations

import itertools
import os
from typing import Optional, Literal, Dict, List, Union

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, root_validator, validator, PrivateAttr

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType


class NavItem(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        type (Literal["navitem"]): Defaults to `"navitem"`.
        pages (NavPagesType): See [NavPagesType][vizro.models.types.NavPagesType].
        icon (str): Name of the icon from the Google Material Icon library. For more available
            icons visit [Google Material Icon library](https://fonts.google.com/icons).
        text (Optional[str]): Text to be displayed below the icon. It automatically gets truncated to the
            `max_text_length`. Defaults to `None`.
    """

    type: Literal["navitem"] = "navitem"  # AM: nav_item?
    pages: Optional[NavPagesType] = []
    text: str = Field(
        ..., description="Text to be displayed below the icon."
    )  # Maybe call label. This just does tooltip for now.
    icon: Optional[str] = Field(None, description="Icon name from Google Material Icon library.")

    _selector: Accordion = PrivateAttr()

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call  # can't do this in validator since it's private?
    def pre_build(self):
        from vizro.models._navigation.accordion import Accordion

        self._selector = Accordion(pages=self.pages)  # type: ignore[arg-type]

    @_log_call
    def build(self, *, active_page_id=None):
        # _selector is an Accordion, so _selector._pages is guaranteed to be Dict[str, List[str]].
        # AM: refactor to make private property for this in Accordion etc.
        all_page_ids = list(itertools.chain(*self._selector.pages.values()))
        first_page_id = all_page_ids[0]
        item_active = active_page_id in all_page_ids

        try:
            first_page = dash.page_registry[first_page_id]
        except KeyError as exc:
            raise KeyError(
                f"Page with ID {first_page_id} cannot be found. Please add the page to `Dashboard.pages`"
            ) from exc

        # remove nesting nav-icon-text now no text?
        button = dbc.Button(
            [
                html.Div(html.Span(self.icon, className="material-symbols-outlined"), className="nav-icon-text"),
                dbc.Tooltip(html.P(self.text), target=self.id, placement="bottom", className="custom-tooltip"),
            ],
            id=self.id,
            className="icon-button",
            href=first_page["relative_path"],
            active=item_active,
        )

        # Only build the selector (id="nav_panel_outer") if the item is active.
        if item_active:
            return html.Div([button, item._selector.build(active_page_id=active_page_id)])

        return button
