from __future__ import annotations

from typing import Annotated, Optional, Union

from pydantic import Field, validator

import dash
from pydantic import PrivateAttr, validator

from vizro._constants import MODULE_PAGE_404
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.accordion import Accordion
from vizro.models._navigation.nav_bar import NavBar
from vizro.models.types import NavigationPagesType

NavigationSelectorType = Annotated[Union[Accordion, NavBar], Field(discriminator="type", description="...")]
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

    if pages is None:
        return [page for page in dash.page_registry.keys() if page != MODULE_PAGE_404]

    return pages


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
        selector (Optional[NavigationSelectorType])
    """

    pages: Optional[NavigationPagesType] = None
    selector: Optional[NavigationSelectorType] = None

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        self._set_selector()

    def _set_selector(self):
        if self.selector is None:
            self.selector = Accordion(pages=self.pages)

    @_log_call
    def build(self, page_id):
        if isinstance(self.selector, NavBar):
            return self.selector.build(page_id=page_id)
        if isinstance(self.selector, Accordion):
            return None, self.selector.build(page_id=page_id)
