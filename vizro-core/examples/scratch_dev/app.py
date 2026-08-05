"""Scratch demo app."""

import vizro.models as vm
import vizro.actions as va
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_1 = vm.Page(
    title="Regular page",
    components=[
        vm.Graph(id="graph_1", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", visible=True),
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
    title="Plain containers",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Container(
                    title="",
                    components=[
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_4"
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
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_4"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
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

page_3 = vm.Page(
    title="Filled containers",
    components=[
        vm.Container(
            title="Outer container plain",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Container(
                    title="Inner container filled",
                    components=[
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_5"
                        ),
                    ],
                    variant="filled",
                    controls=[
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                    ],
                ),
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_5"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
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

page_4 = vm.Page(
    title="Containers nested mixed",
    components=[
        vm.Container(
            title="Outer container filled",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Container(
                    title="Inner container plain",
                    components=[
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_6"
                        ),
                    ],
                    controls=[
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                    ],
                ),
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_6"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
            controls=[
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
            ],
            variant="filled",
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
    title="Containers nested filled",
    components=[
        vm.Container(
            title="Outer container filled",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text"),
                vm.Container(
                    title="Inner container filled",
                    components=[
                        vm.Graph(
                            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_7"
                        ),
                    ],
                    controls=[
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                        vm.Filter(column="species"),
                    ],
                    variant="filled",
                ),
                vm.Button(text="Export", actions=[va.export_data(targets=["graph_7"])], icon="download"),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3], [4, 4, 4, 4], [4, 4, 4, 4], [4, 4, 4, 4], [5, -1, -1, -1]]),
            controls=[
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
                vm.Filter(column="species"),
            ],
            variant="filled",
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

page_6 = vm.Page(
    title="Simple filled container",
    components=[
        vm.Container(
            title="Filled",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_8"),
            ],
            variant="filled",
        )
    ],
)

page_7 = vm.Page(
    title="Simple outlined container",
    components=[
        vm.Container(
            title="Outlined",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"), id="graph_9"),
            ],
            variant="outlined",
        )
    ],
)


dashboard = vm.Dashboard(
    title="Vizro",
    pages=[page_1, page_2, page_6, page_7, page_3, page_4, page_5],
    # navigation=vm.Navigation(nav_selector=vm.NavBar()),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
