from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

from dash import dcc, html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models._components import SubPage


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    tabs: List[SubPage] = []  # LQ: Shall we rename to subpage, tabs, components?

    @_log_call
    def build(self):
        return html.Div(
            [
                dcc.Tabs(
                    id=self.id,
                    children=[
                        dcc.Tab(
                            html.Div(children=[subpage.build()]),
                            id=subpage.title,
                            label=subpage.title,
                        )
                        for subpage in self.tabs
                    ],
                    className="tabs_container",
                ),
            ],
            className="tabs_container_outer",
        )
