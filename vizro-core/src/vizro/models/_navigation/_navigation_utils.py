import itertools

from vizro.managers import model_manager


def _validate_pages(pages):
    """Validator for re-use in `Navigation` and `Accordion` to validate pages."""
    from vizro.models import Page

    if not pages:
        raise ValueError("Ensure this value has at least 1 item.")

    # Ideally we would use dash.page_registry or maybe dashboard.pages here, but we only register pages in
    # dashboard.pre_build and model manager cannot find a Dashboard at validation time.
    # page[0] gives the page model ID.
    registered_pages = [page[0] for page in model_manager._items_with_type(Page)]
    provided_pages = list(itertools.chain(*pages.values())) if isinstance(pages, dict) else pages

    if unknown_pages := [page for page in provided_pages if page not in registered_pages]:
        raise ValueError(f"Unknown page ID {unknown_pages} provided to argument 'pages'.")
    return pages
