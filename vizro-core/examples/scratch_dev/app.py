"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro._themes._color_values import COLORS
import dash_bootstrap_components as dbc
from dash import html

from typing import Literal

from dash import html

import vizro.models as vm
from vizro import Vizro

class Tooltip(vm.VizroBaseModel):
    type: Literal["tooltip"] = "tooltip"

    def build(self):
        return html.Div(
        [
            dbc.Button("Button", id="tooltip-target"),
            dbc.Tooltip("This is a tooltip", target="tooltip-target", is_open=True,
            ),
        ]
)


vm.Page.add_type("components", Tooltip)

page = vm.Page(
    title="Custom Component",
    components=[Tooltip()
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
