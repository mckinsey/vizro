import itertools
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
from dash import get_relative_path, html
from pydantic import AfterValidator, BeforeValidator, Field, model_validator

from vizro._constants import ACCORDION_DEFAULT_TITLE
from vizro.managers._model_manager import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, validate_icon
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models.types import ModelID


def _validate_icons(icons: dict[str, str]) -> dict[str, str]:
    """Validate and normalize each icon name in the mapping."""
    result = {}
    for k, v in icons.items():
        normalized = validate_icon(v)
        if not normalized:
            raise ValueError(
                f"Accordion 'icons' values must be non-empty Material icon names. Got empty value for group '{k}'."
            )
        result[k] = normalized
    return result


def coerce_pages_type(pages: Any) -> dict[Any, Any]:
    if isinstance(pages, dict):
        return pages
    return {ACCORDION_DEFAULT_TITLE: pages}


class Accordion(VizroBaseModel):
    """Accordion to be used as `nav_selector` in [`Navigation`][vizro.models.Navigation]
    or as the nested accordion in a [`NavLink`][vizro.models.NavLink] (when pages is a dict).

    Abstract: Usage documentation
        [How to use an accordion](../user-guides/navigation.md/#group-pages)

    """

    type: Literal["accordion"] = "accordion"
    pages: Annotated[
        dict[
            str,
            list[ModelID],  # TODO[MS]:this is the type after validation, but the type before validation is NavPagesType
        ],
        AfterValidator(_validate_pages),
        BeforeValidator(coerce_pages_type),
        Field(default={}, description="Mapping from name of a pages group to a list of page IDs/titles."),
    ]
    icons: Annotated[
        dict[str, str],
        AfterValidator(_validate_icons),
        Field(
            default_factory=dict,
            description="Optional mapping from group name to Material icon name. Renders icon + title on each header.",
        ),
    ]

    @model_validator(mode="after")
    def _icons_keys_must_be_page_groups(self):
        """Ensure every icons key is a valid page group (key in pages). Skipped when pages is empty (e.g. NavLink)."""
        if not self.pages or not self.icons:
            return self
        page_groups = set(self.pages)
        invalid = set(self.icons) - page_groups
        if invalid:
            raise ValueError(
                f"Accordion 'icons' keys must be page group names. Unknown group(s): {sorted(invalid)}. "
                f"Valid groups: {sorted(page_groups)}."
            )
        return self

    @_log_call
    def build(self, *, active_page_id=None):
        # Build contract: return a single component with id="nav-panel" (Navigation wraps with nav-bar placeholder).
        # UI is implemented with dbc; the Accordion model API (pages, icons) is stable for a future dmc swap.
        # Hide navigation panel if there is only one page
        if len(list(itertools.chain(*self.pages.values()))) == 1:
            return dbc.Nav(id="nav-panel", className="d-none invisible")

        accordion_items = []
        for page_group, page_members in self.pages.items():
            nav_links = self._create_nav_links(pages=page_members)
            icon_name = self.icons.get(page_group)
            title_content: str | list = (
                [html.Span(icon_name, className="material-symbols-outlined accordion-item-icon"), " ", page_group]
                if icon_name
                else page_group
            )
            accordion_items.append(
                dbc.AccordionItem(
                    children=nav_links,
                    title=title_content,
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
