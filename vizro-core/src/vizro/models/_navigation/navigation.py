from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _validate_pages
from vizro.models.types import NavigationPagesType

if TYPE_CHECKING:
    from vizro.models._navigation._accordion import Accordion


class Navigation(VizroBaseModel):
    """Navigation in [`Dashboard`][vizro.models.Dashboard] to structure [`Pages`][vizro.models.Page].

    Args:
        pages (Optional[NavigationPagesType]): See [`NavigationPagesType`][vizro.models.types.NavigationPagesType].
            Defaults to `None`.
    """

    pages: Optional[NavigationPagesType] = None
    _selector: Accordion = PrivateAttr()

    # validators
    _validate_pages = validator("pages", allow_reuse=True)(_validate_pages)

    @_log_call
    def pre_build(self):
        from vizro.models._navigation._accordion import Accordion

        self._selector = Accordion(pages=self.pages)  # type: ignore[arg-type]

    @_log_call
    def build(self, *, active_page_id=None):
        return self._selector.build(active_page_id=active_page_id)
