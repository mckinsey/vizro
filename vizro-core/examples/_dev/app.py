"""Rough example used by developers."""

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, export_original_data, filter_interaction

iris = px.data.iris()

page = vm.Page(
    title="Page Example",
    components=[
        vm.Graph(
            id="scatter_1",
            figure=px.scatter(data_frame=iris, x="sepal_length", y="petal_length", color="species", custom_data=["species"]),
            actions=[
                vm.Action(function=filter_interaction(targets=["scatter_2"])),
            ]
        ),
        vm.Graph(
            id="scatter_2",
            figure=px.scatter(data_frame=iris, x="sepal_length", y="petal_length", color="species"),
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(
                    function=export_original_data(targets=["scatter_2"])
                )
            ]
        )
    ],
    controls=[
        vm.Filter(column="species"),
        # vm.Filter(column="species"),
        # vm.Filter(column="species"),
    ]
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
