from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional, Union, List, Dict, Any

from pydantic import PrivateAttr, validator

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import NavigationPagesType
import dash
from dash import html
import dash_bootstrap_components as dbc

if TYPE_CHECKING:
    from vizro.models._navigation.accordion import Accordion


class Icon(VizroBaseModel):
    """A navigation model in [Dashboard][src.vizro.models.Icon].
    Args:
    name (str): Title to be displayed.
    href (Optional[str]): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to None.
    children (list): list of pages or list of accordions.
    """
    title: Optional[str]
    src: Optional[str]  # src matches html.Img attribute name but maybe call it something else?
    # pages: Optional[Union[str], List[str], Dict[str, List[str]]]  # note can have single string to make it link to just one page
    pages: Optional[Union[List[str], Dict[str, List[str]]]]
    selector: Accordion = None

    @_log_call
    def pre_build(self):
        self._set_selector()

    def _set_selector(self):
        from vizro.models._navigation.accordion import Accordion
        if self.selector is None:
            self.selector = Accordion(pages=self.pages)

    @_log_call
    def build(self):

        icon = dbc.Button(
            children=html.Img(
                src=self.src,
                width=24,
                height=24,
                className="icon",
            ),
            className="icon_button",
            href=self._get_page_href(),
        )
        return icon

    def _get_page_href(self):
        if self.pages:
            if isinstance(self.pages, dict):
                first_page = next(iter(self.selector.pages.values()))[0]
            else:
                first_page = self.pages[0]

            for page in dash.page_registry.values():
                if page["module"] == first_page:
                    return page["relative_path"]
