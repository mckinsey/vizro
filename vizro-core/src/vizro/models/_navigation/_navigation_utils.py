from __future__ import annotations

import itertools
from typing import TypedDict

from dash import html

from vizro.managers import model_manager


def _validate_pages(pages):
    """Reusable validator to check if provided Page IDs exist as registered pages."""
    from vizro.models import Page

    pages_as_list = list(itertools.chain(*pages.values())) if isinstance(pages, dict) else pages
    # Ideally we would use dash.page_registry or maybe dashboard.pages here, but we only register pages in
    # dashboard.pre_build and model manager cannot find a Dashboard at validation time.
    # page[0] gives the page model ID.
    registered_pages = [page[0] for page in model_manager._items_with_type(Page)]

    if not pages_as_list:
        raise ValueError("Ensure this value has at least 1 item.")

    if unknown_pages := [page for page in pages_as_list if page not in registered_pages]:
        raise ValueError(f"Unknown page ID {unknown_pages} provided to argument 'pages'.")
    return pages


# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
class _NavBuildType(TypedDict):
    nav_bar_outer: html.Div
    nav_panel_outer: html.Div
