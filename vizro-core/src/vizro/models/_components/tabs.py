from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from dash import dcc, html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models._components import Tab


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    title: str
    tabs: List[Tab] = []

    @_log_call
    def build(self):
        return html.Div(
            [html.H3(self.title), dcc.Tabs(id=self.id, children=[tab.build() for tab in self.tabs])],
            className="tabs_container",
        )
