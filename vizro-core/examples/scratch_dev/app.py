"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
import dash_bootstrap_components as dbc

df = px.data.iris()

page = vm.Page(
    title="Bootstrap theme inside Vizro app",
    layout=vm.Flex(),
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", height=600),
                )
            ],
            variant="filled",
        ),
        vm.Container(
            components=[
                vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species", height=600))
            ],
            variant="filled",
        ),
    ],
    controls=[vm.Filter(column="species"), vm.Filter(column="petal_length"), vm.Filter(column="sepal_width")],
)

dashboard = vm.Dashboard(pages=[page, vm.Page(title="Page 2", components=[vm.Button()])])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
