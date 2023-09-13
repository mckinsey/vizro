from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional, Union, List, Dict, Any

from pydantic import PrivateAttr, validator
from dash import dcc, html

from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import NavigationPagesType
from vizro.models._navigation.icon import Icon

if TYPE_CHECKING:
    from vizro.models._navigation.accordion import Accordion




class NavBar(VizroBaseModel):
    selector: Optional[Any]
    pages: Optional[Union[List[str], Dict[str, List[str]]]]
    icons: Optional[List[Icon]]
    @_log_call
    def build(self):
        if isinstance(self.pages, list):
            self.selector = [Icon(pages=page) for page in self.pages]
        if self.icons:
            icons = [icon.build() for icon in self.icons]
            icon_bar = html.Div(
                children=icons,
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "width": "56px",
                    "backgroundColor": "gray",
                    "paddingTop": "40px",
                    "alignItems": "center",
                    "gap": "16px"
                }
            )

            return icon_bar