"""Scratch demo app."""

import vizro.models as vm
import vizro.actions as va
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_1 = vm.Page(
    title="Action Logs 1",
    components=[
        vm.Graph(id="graph_1", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
        vm.Button(text="Download data", actions=[va.export_data(targets=["graph_1"])]),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Filter(column="sepal_length"),
        vm.Filter(column="petal_width"),
    ],
)

page_2 = vm.Page(
    title="Action Logs 2",
    components=[
        vm.Graph(id="graph_2", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2],
    navigation=vm.Navigation(nav_selector=vm.NavBar())
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
