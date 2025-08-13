from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import dash_bootstrap_components as dbc
from typing_extensions import TypedDict

from vizro.managers import model_manager
from vizro.models.types import ModelID, NavPagesType

if TYPE_CHECKING:
    from vizro.models import Page

# Error message constants
_AMBIGUOUS_PAGE_ERROR_MSG = (
    "Ambiguous page reference '{page_ref}': Multiple pages found with title '{page_ref}'. "
    "Page IDs: {page_ids}. Page titles must be unique to avoid ambiguity."
)
_UNKNOWN_PAGES_ERROR_MSG = (
    "Unknown page ID or title {unknown_pages} provided to argument 'pages'. Available page titles: {available_titles}"
)
_EMPTY_PAGES_ERROR_MSG = "Ensure this value has at least 1 item."


def _resolve_page_reference(
    page_ref: str, page_by_id: dict[ModelID, Page], pages_by_title: dict[str, list[Page]]
) -> Optional[ModelID]:
    """Resolve a page reference (ID or title) to a page ID."""
    # First check if it's a valid page ID
    if page_ref in page_by_id:
        return page_ref

    # Try to find by title
    if page_ref in pages_by_title:
        matching_pages = pages_by_title[page_ref]
        if len(matching_pages) > 1:
            page_ids = [p.id for p in matching_pages]
            raise ValueError(_AMBIGUOUS_PAGE_ERROR_MSG.format(page_ref=page_ref, page_ids=page_ids))
        return matching_pages[0].id

    # Page not found - return None to collect for batch error
    return None


# This will need to move to pre-build in next PR - hopefully there is no problems
# introduced with handling things this way
def _validate_pages(pages: NavPagesType) -> NavPagesType:  # noqa: PLR0912
    """Reusable validator to check if provided Page titles exist as registered pages."""
    # Build lookup maps in a single pass through all pages
    page_by_id, pages_by_title = model_manager._get_page_lookup_maps()

    # Process pages based on structure (dict or list)
    if isinstance(pages, dict):
        # Check if dict has any pages
        pages_as_list = [page for group_pages in pages.values() for page in group_pages]
        if not pages_as_list:
            raise ValueError(_EMPTY_PAGES_ERROR_MSG)

        validated_dict = {}
        unknown_pages = []

        for group_name, group_pages in pages.items():
            validated_group = []
            for page_ref in group_pages:
                resolved_id = _resolve_page_reference(page_ref, page_by_id, pages_by_title)
                if resolved_id is None:
                    unknown_pages.append(page_ref)
                else:
                    validated_group.append(resolved_id)
            validated_dict[group_name] = validated_group

        if unknown_pages:
            available_titles = list(pages_by_title.keys())
            raise ValueError(
                _UNKNOWN_PAGES_ERROR_MSG.format(unknown_pages=unknown_pages, available_titles=available_titles)
            )

        return validated_dict
    else:
        # Process as list
        if not pages:
            raise ValueError(_EMPTY_PAGES_ERROR_MSG)

        validated_list = []
        unknown_pages = []

        for page_ref in pages:
            resolved_id = _resolve_page_reference(page_ref, page_by_id, pages_by_title)
            if resolved_id is None:
                unknown_pages.append(page_ref)
            else:
                validated_list.append(resolved_id)

        if unknown_pages:
            available_titles = list(pages_by_title.keys())
            raise ValueError(
                _UNKNOWN_PAGES_ERROR_MSG.format(unknown_pages=unknown_pages, available_titles=available_titles)
            )

        return validated_list


# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_NavBuildType = TypedDict("_NavBuildType", {"nav-bar": dbc.Navbar, "nav-panel": dbc.Nav})
