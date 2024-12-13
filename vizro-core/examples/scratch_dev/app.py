"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from typing import List, Literal, Tuple
from vizro.models.types import ControlType
from dash import html


class CustomGroup(vm.VizroBaseModel):
    """Container to group controls."""

    type: Literal["custom_group"] = "custom_group"
    controls: List[Tuple[str, List[ControlType]]] = [[]]

    def build(self):
        return html.Div(
            children=[
                html.Div(
                    children=[html.Br(), html.H5(control_tuple[0]), *[control.build() for control in control_tuple[1]]],
                )
                for control_tuple in self.controls
            ]
        )


vm.Page.add_type("controls", CustomGroup)


page = vm.Page(
    title="Title",
    components=[
        vm.Graph(id="graph_id", figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        CustomGroup(
            controls=[
                (
                    "Categorical Filters",
                    [
                        vm.Filter(column="species"),
                    ],
                ),
                (
                    "Numeric Filters",
                    [
                        vm.Filter(column="petal_length"),
                        vm.Filter(column="sepal_length"),
                    ],
                ),
            ],
        ),
        vm.Parameter(
            targets=["graph_id.x"],
            selector=vm.RadioItems(
                title="Select X Axis",
                options=["sepal_width", "sepal_length", "petal_width", "petal_length"],
                value="sepal_width",
            ),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
