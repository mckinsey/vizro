from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

import dash_mantine_components as dmc
from dash import html
from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models._components import Container


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    tabs: List[Container] = []

    @validator("tabs", always=True)
    def validate_tabs(cls, tabs):
        if not tabs:
            raise ValueError("Ensure this value has at least 1 item.")
        return tabs

    @_log_call
    def build(self):
        return dmc.Tabs(
            id=self.id,
            value=self.tabs[0].id,
            children=[
                dmc.TabsList(
                    [dmc.Tab(tab.title, value=tab.id, className="tab-single") for tab in self.tabs],
                    className="tabs-list",
                ),
            ]
            + [
                dmc.TabsPanel(html.Div(children=[tab.build()], className="tabs_panel", style={"height": "100%"}),
                              value=tab.id, style={"height": "100%"})
                for tab in self.tabs
            ],
            persistence=True,
            style={"height": "100%"},
        )
