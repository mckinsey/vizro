from __future__ import annotations

from collections import defaultdict
from itertools import chain
from typing import Optional

import dash_bootstrap_components as dbc
from typing_extensions import TypedDict

from vizro.managers import model_manager
from vizro.models.types import ModelID, NavPagesType

# Error message constants
_AMBIGUOUS_PAGE_ERROR_MSG = (
    "Ambiguous page reference '{page_ref}': Multiple pages found with title '{page_ref}'. "
    "Page IDs: {page_ids}. You should refer to these pages by ID to avoid ambiguity."
)
_UNKNOWN_PAGES_ERROR_MSG = (
    "Unknown page ID or title {unknown_pages} provided to argument 'pages'. Available page titles: {available_titles}"
)
_EMPTY_PAGES_ERROR_MSG = "Ensure this value has at least 1 item."


def _resolve_page_reference(
    page_ref: str,
    title_to_ids: dict[str, list[ModelID]],
) -> Optional[ModelID]:
    """Resolve a page reference (ID or title) to a page ID."""
    # First check if it's a valid page ID
    page_ids = chain.from_iterable(title_to_ids.values())

    if page_ref in page_ids:
        return page_ref

    # Try to find by title
    matching_pages = title_to_ids.get(page_ref)
    if not matching_pages:
        return None
    if len(matching_pages) > 1:
        raise ValueError(_AMBIGUOUS_PAGE_ERROR_MSG.format(page_ref=page_ref, page_ids=matching_pages))
    return matching_pages[0]


def _resolve_list_of_page_references(
    page_ref_list: list[str], title_to_ids: dict[str, list[ModelID]]
) -> tuple[list[str], list[ModelID]]:
    """Resolve a list of page references to page IDs."""
    unknown_pages: list[str] = []
    validated_list: list[ModelID] = []

    for page_ref in page_ref_list:
        resolved_ref = _resolve_page_reference(page_ref, title_to_ids)
        if resolved_ref is None:
            unknown_pages.append(page_ref)
        else:
            validated_list.append(resolved_ref)
    return unknown_pages, validated_list


# TODO[MS]: This will need to move to pre-build in next PR - hopefully there is no problems
# introduced with handling things this way
def _validate_pages(pages: NavPagesType) -> NavPagesType:
    """Reusable validator to check if provided Page titles exist as registered pages."""
    from vizro.models import Page

    # Build lookup map for pages by title
    title_to_ids: dict[str, list[ModelID]] = defaultdict(list)
    for page in model_manager._get_models(Page):
        title_to_ids[page.title].append(page.id)

    # Process pages based on structure (dict or list)
    unknown_pages: list[str] = []

    if isinstance(pages, dict):
        if not any(pages.values()):
            raise ValueError(_EMPTY_PAGES_ERROR_MSG)

        validated_dict = {}

        for group_name, group_pages in pages.items():
            group_unknown_pages, validated_list_in_group = _resolve_list_of_page_references(group_pages, title_to_ids)
            validated_dict[group_name] = validated_list_in_group
            unknown_pages.extend(group_unknown_pages)

    else:
        if not pages:
            raise ValueError(_EMPTY_PAGES_ERROR_MSG)

        unknown_pages, validated_list = _resolve_list_of_page_references(pages, title_to_ids)

    if unknown_pages:
        available_titles = list(title_to_ids.keys())
        raise ValueError(
            _UNKNOWN_PAGES_ERROR_MSG.format(unknown_pages=unknown_pages, available_titles=available_titles)
        )
    return validated_dict if isinstance(pages, dict) else validated_list


# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_NavBuildType = TypedDict("_NavBuildType", {"nav-bar": dbc.Navbar, "nav-panel": dbc.Nav})
