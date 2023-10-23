from __future__ import annotations

from typing import List, Optional

from dash import html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import ComponentType


# LQ: What should the final naming be? SubPage, Container, ...
class SubPage(VizroBaseModel):
    components: List[ComponentType]
    title: Optional[str]
    # layout: Optional[Layout]

    @_log_call
    def build(self):
        components = [component.build() for component in self.components]
        return html.Div(children=[html.H3(self.title), *components], id=self.id, className="subpage-container")
