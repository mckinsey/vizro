from __future__ import annotations

import itertools
from typing import Optional

import dash
import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field, PrivateAttr, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models.types import NavPagesType


class NavLink(VizroBaseModel):
    """Icon to be used in Navigation Panel of Dashboard.

    Args:
        ages (Optional[NavPagesType]): See [`NavPagesType`][vizro.models.types.NavPagesType].
            Defaults to `[]`.
        label (str): Text description of the icon for use in tooltip.
        icon (Optional[str]): Icon name from [Google Material icons library](https://fonts.google.com/icons).
            Defaults to `None`.

    """

    pages: NavPagesType = []
    label: str = Field(..., description="Text description of the icon for use in tooltip.")
    icon: Optional[str] = Field(None, description="Icon name from Google Material icons library.")

    _nav_selector: Accordion = PrivateAttr()

    # Re-used validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        from vizro.models._navigation.accordion import Accordion

        self._nav_selector = Accordion(pages=self.pages)  # type: ignore[arg-type]

    @_log_call
    def build(self, *, active_page_id=None):
        # _nav_selector is an Accordion, so _nav_selector._pages is guaranteed to be Dict[str, List[str]].
        all_page_ids = list(itertools.chain(*self._nav_selector.pages.values()))
        first_page_id = all_page_ids[0]
        item_active = active_page_id in all_page_ids

        try:
            first_page = dash.page_registry[first_page_id]
        except KeyError as exc:
            raise KeyError(
                f"Page with ID {first_page_id} cannot be found. Please add the page to `Dashboard.pages`"
            ) from exc

        button = dbc.Button(
            [
                html.Span(self.icon, className="material-symbols-outlined"),
                # TODO: commented out until we insert styling for the tooltip or find a better way to display it (e.g.
                # try dbc.Popover or Dash mantine components tooltip?).
                # dbc.Tooltip(html.P(self.label), target=self.id, placement="bottom", className="custom-tooltip"),
            ],
            id=self.id,
            className="icon-button",
            href=first_page["relative_path"],
            active=item_active,
        )

        # Only build the nav_selector (id="nav_panel_outer") if the item is active.
        if item_active:
            return html.Div([button, self._nav_selector.build(active_page_id=active_page_id)])

        return html.Div(button)
