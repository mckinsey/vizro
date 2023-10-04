import warnings

import dash

from vizro._constants import MODULE_PAGE_404
from vizro.managers import model_manager


# Validator for re-use in other models to validate pages
# TODO: Adjust validator to take into account pages on different icons
def _validate_pages(pages):
    from vizro.models import Page
    registered_pages = [page[0] for page in model_manager._items_with_type(Page)]

    if pages is None:
        return registered_pages

    if not pages:
        raise ValueError("Ensure this value has at least 1 item.")

    if isinstance(pages, dict):
        missing_pages = [
            page
            for page in registered_pages
            if page not in {page for nav_pages in pages.values() for page in nav_pages}
        ]
        unknown_pages = [page for nav_pages in pages.values() for page in nav_pages if page not in registered_pages]
    else:
        missing_pages = [page for page in registered_pages if page not in pages]
        unknown_pages = [page for page in pages if page not in registered_pages]

    if missing_pages:
        warnings.warn(
            f"Not all registered pages used in Navigation 'pages'. Missing pages {missing_pages}!", UserWarning
        )

    if unknown_pages:
        raise ValueError(
            f"Unknown page ID or page title provided to Navigation 'pages'. " f"Unknown pages: {unknown_pages}"
        )
    return pages