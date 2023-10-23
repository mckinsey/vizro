from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

import dash_mantine_components as dmc
from dash import html

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models._components import SubPage


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    tabs: List[SubPage] = []  # LQ: Shall we rename to subpage, tabs, components?

    @_log_call
    def build(self):
        return dmc.Tabs(
            id=self.id,
            children=[
                dmc.TabsList(
                    [dmc.Tab(subpage.title, value=subpage.id, className="tab-single") for subpage in self.tabs],
                    className="tabs-list",
                ),
            ]
            + [dmc.TabsPanel(html.Div(children=[subpage.build()]), value=subpage.id) for subpage in self.tabs],
        )
