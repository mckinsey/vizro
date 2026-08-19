"""Scratch demo app."""

import vizro.models as vm
import vizro.actions as va
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()

page_1 = vm.Page(
    title="Simple filled container",
    components=[
        vm.Container(
            title="Filled",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            variant="filled",
            layout=vm.Grid(grid=[[0, 1, 1, 1]]),
        )
    ],
)

page_2 = vm.Page(
    title="Nested mixed containers",
    components=[
        vm.Container(
            title="Outer plain container",
            components=[
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Container(
                    title="Inner container filled",
                    components=[
                        vm.Card(text="Placeholder text"),
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_2"
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
                    controls=[
                        vm.Filter(column="species"),
                    ],
                    variant="filled",
                ),
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_2"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
            controls=[
                vm.Filter(column="species"),
            ],
        )
    ],
)

page_3 = vm.Page(
    title="Nested filled containers",
    components=[
        vm.Container(
            title="Outer filled container",
            components=[
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Container(
                    title="Inner container filled",
                    components=[
                        vm.Card(text="Card text"),
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_1"
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 1, 1, 1]]),
                    controls=[
                        vm.Filter(column="species"),
                    ],
                    variant="filled",
                ),
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_1"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
            controls=[
                vm.Filter(column="species"),
            ],
            variant="filled",
        )
    ],
)


dashboard = vm.Dashboard(
    title="Vizro",
    pages=[page_1, page_2, page_3],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
