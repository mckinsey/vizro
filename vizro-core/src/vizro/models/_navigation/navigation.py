from __future__ import annotations

import itertools
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
def _validate_pages(pages, registered_pages):
    from vizro.models import Page

    # Ideally we would use dash.page_registry or maybe dashboard.pages here, but we only register pages in
    # dashboard.pre_build.
    # page[0] gives the page model ID.
    registered_pages = [page[0] for page in model_manager._items_with_type(Page)]
    # _, dashboard = next(model_manager._items_with_type(Dashboard))
    # registered_pages = dashboard.pages

    # Probably don't need this any more:
    # if pages is None:
    #     return registered_pages

    if not pages:
        raise ValueError("Ensure this value has at least 1 item.")

    if isinstance(pages, dict):
        pages = list(itertools.chain(pages.values()))
    # now guaranteed that pages is a list

    if (unknown_pages := [page for page in pages if page not in registered_pages]):
        raise ValueError(
            f"Unknown page ID or page title provided to Navigation 'pages'. " f"Unknown pages: {unknown_pages}"
        )
    return pages


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavigationPagesType]): See [`NavigationPagesType`][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """
    pages: Optional[NavigationPagesType] = None
    _selector: Accordion = PrivateAttr()

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)
    # does this set to all pages also?

    @_log_call
    def pre_build(self):
        from vizro.models._navigation._accordion import Accordion

        self._selector = Accordion(pages=self.pages)

    @_log_call
    def build(self, *, active_page_id=None):
        return self._selector.build(active_page_id=active_page_id)
