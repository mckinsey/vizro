from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models._navigation.nav_bar import NavBar
from vizro.models.types import NavigationPagesType

if TYPE_CHECKING:
    from vizro.models._navigation.accordion import Accordion


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavigationPagesType]): See [NavigationPagesType][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """

    pages: Optional[NavigationPagesType] = None
    selector: Optional[Union[Accordion, NavBar]] = None

    # validators
    _validate_pages = validator("pages", allow_reuse=True, always=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        self._set_selector()

    def _set_selector(self):
        from vizro.models._navigation.accordion import Accordion

        if self.selector is None:
            self.selector = Accordion(pages=self.pages)

    @_log_call
    def build(self, page_id):
        if isinstance(self.selector, NavBar):
            return self.selector.build(page_id=page_id)
        return self.selector.build()
