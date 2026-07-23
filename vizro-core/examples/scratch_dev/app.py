"""Scratch demo app."""

import vizro.models as vm
import vizro.actions as va
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_1 = vm.Page(
    title="Action Logs 1",
    components=[
        vm.Container(
            title="",
            components=[
                # vm.Card(text="placeholder text"),
                vm.Graph(id="graph_3", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"))
            ],
            variant="filled",
            controls=[vm.Filter(column="species")],
        ),
        vm.Graph(id="graph_1", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.ControlGroup(
            title="Control group 1",
            controls=[
                vm.Filter(column="sepal_length"),
            ],
            description="control group info",
        ),
        vm.ControlGroup(
            title="Control group 2",
            controls=[
                vm.Filter(column="petal_width"),
            ],
            description="control group info",
        ),
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
    title="Vizro",
    pages=[page_1, page_2],
    # navigation=vm.Navigation(nav_selector=vm.NavBar()),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
