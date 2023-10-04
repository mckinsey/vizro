from __future__ import annotations

from typing import Annotated, Optional, Union

from pydantic import Field, validator

from pydantic import PrivateAttr, validator

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
    def build(self, active_page_id):
        if isinstance(self.selector, NavBar):
            return self.selector.build(active_page_id=active_page_id)
        if isinstance(self.selector, Accordion):
            return None, self.selector.build(active_page_id=active_page_id)
