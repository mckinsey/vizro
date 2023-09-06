from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr, validator

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import NavigationPagesType

if TYPE_CHECKING:
    from vizro.models._navigation._accordion import Accordion


# Validator for re-use in other models to validate pages
def _validate_pages(pages):
    from vizro.models import Page

    if pages is not None and not pages:
        raise ValueError("Ensure this value has at least 1 item.")

    if pages:
        registered_pages = [page[0] for page in model_manager._items_with_type(Page)]

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


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """

    pages: Optional[NavigationPagesType] = None
    _selector: Accordion = PrivateAttr()

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        self._set_selector()

    def _set_selector(self):
        from vizro.models._navigation._accordion import Accordion

        self._selector = Accordion(pages=self.pages)

    @_log_call
    def build(self):
        return self._selector.build()
