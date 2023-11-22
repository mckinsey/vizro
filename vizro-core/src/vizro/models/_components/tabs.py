from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

import dash_mantine_components as dmc
from dash import html
from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models._components import SubPage


class Tabs(VizroBaseModel):
    type: Literal["tabs"] = "tabs"
    subpages: List[SubPage] = []  # LQ: Shall we rename to subpage, tabs, components, container?

    @validator("subpages", always=True)
    def validate_subpages(cls, subpages):
        if not subpages:
            raise ValueError("Ensure this value has at least 1 item.")
        return subpages

    @_log_call
    def build(self):
        return dmc.Tabs(
            id=self.id,
            value=self.subpages[0].id,
            children=[
                dmc.TabsList(
                    [dmc.Tab(subpage.title, value=subpage.id, className="tab-single") for subpage in self.subpages],
                    className="tabs-list",
                ),
            ]
            + [
                dmc.TabsPanel(html.Div(children=[subpage.build()], className="tabs_panel", style={"height": "100%"}),
                              value=subpage.id, style={"height": "100%"})
                for subpage in self.subpages
            ],
            persistence=True,
            style={"height": "100%"},
        )
