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
    text: str = "This is a tooltip"

    def build(self):
        return html.Div(
        [
            dbc.Button("Button", id=f"{self.id}-tooltip-target"),
            dbc.Tooltip(self.text, target=f"{self.id}-tooltip-target", is_open=True,
            ),
        ]
)


vm.Page.add_type("components", Tooltip)

page = vm.Page(
    title="Custom Component",
    components=[
        Tooltip(text="Tooltip label"),
        Tooltip(text="Max. width of tooltip should not exceed 180px - this instance should be used for multiple lines of text for increased legibility.")
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
