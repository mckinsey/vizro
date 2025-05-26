import itertools
from collections.abc import Mapping
from typing import Annotated, Literal, cast

import dash_bootstrap_components as dbc
from dash import get_relative_path
from pydantic import AfterValidator, BeforeValidator, Field

from vizro._constants import ACCORDION_DEFAULT_TITLE
from vizro.managers._model_manager import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models.types import ModelID


def coerce_pages_type(pages):
    if isinstance(pages, Mapping):
        return pages
    return {ACCORDION_DEFAULT_TITLE: pages}


class Accordion(VizroBaseModel):
    """Accordion to be used as nav_selector in [`Navigation`][vizro.models.Navigation].

    Args:
        type (Literal["accordion"]): Defaults to `"accordion"`.
        pages (dict[str, list[ModelID]]): Mapping from name of a pages group to a list of page IDs. Defaults to `{}`.

    """

    type: Literal["accordion"] = "accordion"
    pages: Annotated[
        dict[
            str,
            list[ModelID],  # TODO[MS]:this is the type after validation, but the type before validation is NavPagesType
        ],
        AfterValidator(_validate_pages),
        BeforeValidator(coerce_pages_type),
        Field(default={}, description="Mapping from name of a pages group to a list of page IDs."),
    ]

    @_log_call
    def build(self, *, active_page_id=None):
        # Note build does not return _NavBuildType but just a single html.Div with id="nav-panel".
        # Hide navigation panel if there is only one page
        if len(list(itertools.chain(*self.pages.values()))) == 1:
            return dbc.Nav(id="nav-panel", className="d-none invisible")

        accordion_items = []
        for page_group, page_members in self.pages.items():
            nav_links = self._create_nav_links(pages=page_members)
            accordion_items.append(
                dbc.AccordionItem(
                    children=nav_links,
                    title=page_group.upper(),
                    class_name="accordion-item-header",
                    item_id=page_group,
                )
            )

        active_item = next(
            (page_group for page_group, page_members in self.pages.items() if active_page_id in page_members), None
        )

        return dbc.Nav(
            children=[
                dbc.Accordion(
                    id=self.id,
                    children=accordion_items,
                    class_name="accordion",
                    persistence=True,
                    persistence_type="session",
                    always_open=True,
                    # `active_item` is required to open the accordion automatically when navigating from a homepage
                    # to any of the pages in the accordion.
                    active_item=active_item,
                )
            ],
            id="nav-panel",
        )

    def _create_nav_links(self, pages: list[ModelID]):
        """Creates a `NavLink` for each provided page."""
        from vizro.models import Page

        nav_links = []

        for page_id in pages:
            page = cast(Page, model_manager[page_id])
            nav_links.append(
                dbc.NavLink(
                    children=page.title,
                    className="accordion-item-link",
                    active="exact",
                    href=get_relative_path(page.path),
                )
            )
        return nav_links
