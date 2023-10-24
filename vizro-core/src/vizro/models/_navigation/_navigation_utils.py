import itertools

from vizro.managers import model_manager


def _validate_pages(pages):
    """Reusable validator to check if provided Page IDs exist as registered pages."""
    from vizro.models import Page

    pages_as_list = list(itertools.chain(*pages.values())) if isinstance(pages, dict) else pages

    if not pages_as_list:
        raise ValueError("Ensure this value has at least 1 item.")

    # Ideally we would use dash.page_registry or maybe dashboard.pages here, but we only register pages in
    # dashboard.pre_build and model manager cannot find a Dashboard at validation time.
    # page[0] gives the page model ID.
    registered_pages = [page[0] for page in model_manager._items_with_type(Page)]
    if unknown_pages := [page for page in pages_as_list if page not in registered_pages]:
        raise ValueError(f"Unknown page ID {unknown_pages} provided to argument 'pages'.")
    return pages
