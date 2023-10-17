from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, dcc

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
        @callback(
            Output("tab-content", "children"),
            [Input(self.id, "active_tab")],
        )
        def render_tab_content(active_tab):
            """
            This callback takes the 'active_tab' property as input, as well as the
            stored graphs, and renders the tab content depending on what the value of
            'active_tab' is.
            """
            # tab_1 = html.Div(children=[html.H3("Tab 1 Title", className="tab-title"), dcc.Loading(
            #      dcc.Graph(figure={"data": [{"x": [10, 20, 30], "y": [10, 40, 90]}]})
            #  )])
            #
            # tab_2 = html.Div(children=[html.H3("Tab 2 Title", className="tab-title"), dcc.Loading(
            #     dcc.Graph(figure={"data": [{"x": [10, 20, 30], "y": [10, 40, 90]}]})
            # )])
            #
            # if active_tab == "tab-1":
            #     print(tab_1)
            #     return tab_1
            # if active_tab == "tab-2":
            #     return tab_2
            # return "No tab selected"
            for tab in self.tabs:
                print(f"active_tab: {active_tab}")
                print(f"tab.id: {tab.id}")
                if active_tab == tab.id:
                    tab_build = tab.build()
                    print(f"tab.build(): {tab_build}")
                    return tab_build
            return "No Tab selected."

        return html.Div(
            [
                html.H3(self.title),
                dbc.Tabs(id=self.id,
                         children=[tab.pre_build() for tab in self.tabs],
                         className="tabs_container",
                         active_tab=self.tabs[0].id),
                html.Div(id="tab-content")
            ],
            className="tabs_container_outer",
        )
