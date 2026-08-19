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
                vm.Card(text="Card text"),
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            variant="filled",
            layout=vm.Grid(grid=[[0, 1, 1, 1]]),
        )
    ],
    controls=[
        vm.Filter(column="species", visible=False),
        vm.Filter(column="sepal_length"),
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
        vm.ControlGroup(
            title="Control group 3",
            controls=[
                vm.Filter(column="sepal_length"),
            ],
            description="control group info",
        ),
        vm.ControlGroup(
            title="Control group 4",
            controls=[
                vm.Filter(column="petal_width"),
            ],
            description="control group info",
        ),
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
            variant="filled",
        )
    ],
)


page_4 = vm.Page(
    title="Plain containers",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Card(text="Card text"),
                vm.Container(
                    title="",
                    components=[
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
                        ),
                        vm.Container(
                            title="",
                            components=[
                                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                            ],
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 0, 1]]),
                ),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4]]),
            controls=[
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
            ],
        )
    ],
    controls=[
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

page_5 = vm.Page(
    title="Simple outlined container",
    components=[
        vm.Container(
            title="Outlined",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            variant="outlined",
        )
    ],
    controls=[vm.Filter(column="species", visible=False)],
)

page_6 = vm.Page(
    title="Containers and vm.Card",
    components=[
        vm.Container(
            title="Container plain",
            components=[vm.Text(text="vm.Text inside plain container")],
        ),
        vm.Container(
            title="Container filled",
            components=[vm.Text(text="vm.Text inside filled container")],
            variant="filled",
        ),
        vm.Card(text="vm.Card in Page.components"),
        vm.Container(
            title="Container plain with card",
            components=[vm.Card(text="vm.Card inside plain container")],
        ),
        vm.Container(
            title="Container filled with card",
            components=[vm.Card(text="vm.Card inside filled container")],
            variant="filled",
        ),
    ],
    layout=vm.Grid(grid=[[0, 1, 2], [3, 4, -1]]),
)


dashboard = vm.Dashboard(
    title="Vizro",
    pages=[page_1, page_2, page_5, page_3, page_4, page_6],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(
                    pages=["Simple filled container", "Nested mixed containers", "Nested filled containers"],
                    label="First icon",
                ),
                vm.NavLink(
                    pages=["Plain containers", "Simple outlined container", "Containers and vm.Card"],
                    label="Second icon",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
