# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


iris = px.data.iris()

page1 = vm.Page(
    title="Page with custom container",
    components=[
        vm.Container(
            id="container_0",
            title="Inline default styling",
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(
                        iris,
                        x="sepal_length",
                        y="petal_width",
                        color="species",
                        custom_data=["species"],
                    ),
                ),
            ],
            variant="filled",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(value=["setosa"], title="Species"),
                ),
                vm.Parameter(
                    targets=["scatter_chart.title"],
                    selector=vm.RadioItems(
                        options=["My scatter chart", "A better title!", "Another title..."], title="Parameter title"
                    ),
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Checklist()),
    ],
)


page2 = vm.Page(
    title="Controls above tabs",
    components=[
        vm.Container(
            title="Container with tabs and controls",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(title="Species", extra={"inline": True}),
                    targets=["graph3", "graph4"],
                )
            ],
            components=[
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Tab1",
                            components=[
                                vm.Graph(
                                    id="graph3",
                                    figure=px.bar(
                                        iris,
                                        x="sepal_length",
                                        y="sepal_width",
                                        color="species",
                                    ),
                                ),
                            ],
                        ),
                        vm.Container(
                            title="Tab2",
                            components=[
                                vm.Graph(
                                    id="graph4",
                                    figure=px.scatter(
                                        iris,
                                        x="sepal_length",
                                        y="petal_width",
                                        color="species",
                                        custom_data=["species"],
                                    ),
                                ),
                            ],
                        ),
                    ]
                )
            ],
        )
    ],
)
page3 = vm.Page(
    title="Controls in the tabs",
    components=[
        vm.Container(
            title="Container with tabs and controls",
            controls=[
                vm.Filter(
                    column="species", selector=vm.Checklist(title="Species", extra={"inline": True}), targets=["graph6"]
                )
            ],
            components=[
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Tab3",
                            components=[
                                vm.Container(
                                    title="Container within tab",
                                    components=[
                                        vm.Graph(
                                            id="graph5",
                                            figure=px.bar(
                                                iris,
                                                x="sepal_length",
                                                y="sepal_width",
                                                color="species",
                                            ),
                                        ),
                                    ],
                                    controls=[
                                        vm.Filter(
                                            column="species",
                                            selector=vm.RadioItems(title="Species", extra={"inline": True}),
                                        )
                                    ],
                                ),
                            ],
                        ),
                        vm.Container(
                            title="Tab4",
                            components=[
                                vm.Graph(
                                    id="graph6",
                                    figure=px.scatter(
                                        iris,
                                        x="sepal_length",
                                        y="petal_width",
                                        color="species",
                                        custom_data=["species"],
                                    ),
                                ),
                            ],
                        ),
                    ]
                )
            ],
        )
    ],
)

page4 = vm.Page(
    title="Container within container",
    components=[
        vm.Container(
            title="Outer container",
            layout=vm.Layout(grid=[[0, 0], [1, 2]]),
            components=[
                vm.Container(
                    title="Inner container",
                    components=[
                        vm.Graph(
                            id="graph9",
                            figure=px.scatter(
                                iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                            ),
                        ),
                    ],
                    controls=[
                        vm.Filter(
                            column="petal_width",
                            selector=vm.RangeSlider(title="Petal width"),
                        ),
                    ],
                    variant="filled",
                ),
                vm.Graph(
                    id="graph7",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species", title="Container I - Bar"),
                ),
                vm.Graph(id="graph10", figure=px.violin(px.data.iris(), x="species", y="sepal_width", box=True)),
            ],
            variant="outlined",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(value=["setosa"], title="Species", extra={"inline": True}),
                ),
            ],
        )
    ],
)

page5 = vm.Page(
    title="Page with dropdown",
    components=[
        vm.Container(
            title="Controls - Dropdown",
            components=[
                vm.Graph(
                    title="Bar chart",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species"),
                ),
                vm.Graph(
                    title="Scatter chart",
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                    ),
                ),
            ],
            layout=vm.Layout(grid=[[0, 1]]),
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(title="Species")),
            ],
            variant="filled",
        )
    ],
)

page6 = vm.Page(
    title="Page with multiple controls",
    components=[
        vm.Container(
            title="Controls - Multiple",
            components=[
                vm.Graph(
                    title="Bar chart",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species"),
                ),
                vm.Graph(
                    title="Scatter chart",
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                    ),
                ),
            ],
            layout=vm.Layout(grid=[[0, 1]]),
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown()),
                vm.Filter(column="species", selector=vm.Checklist()),
                vm.Filter(column="sepal_length", selector=vm.RangeSlider()),
                vm.Filter(column="species", selector=vm.RadioItems()),
            ],
            variant="filled",
        )
    ],
)

page7 = vm.Page(
    title="Normal (not inline) controls at the top of container",
    components=[
        vm.Container(
            title="Controls - Multiple",
            components=[
                vm.Graph(
                    title="Bar chart",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species"),
                ),
                vm.Graph(
                    title="Scatter chart",
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                    ),
                ),
            ],
            layout=vm.Layout(grid=[[0, 1]]),
            controls=[
                vm.Filter(
                    column="species", selector=vm.Checklist(value=["setosa"], title="Species", extra={"inline": False})
                ),
            ],
        )
    ],
)

page8 = vm.Page(
    title="Controls with targets outside of the container",
    components=[
        vm.Container(
            title="Container with control",
            components=[
                vm.Graph(
                    id="bar_chart11",
                    title="Bar chart",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species"),
                ),
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(value=["setosa"], title="Species"),
                    targets=["bar_chart11", "scatter_chart11"],
                ),
            ],
        ),
        vm.Container(
            title="Container with target",
            components=[
                vm.Graph(
                    title="Scatter chart",
                    id="scatter_chart11",
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                    ),
                ),
            ],
        ),
    ],
)

page9 = vm.Page(
    title="Page with multiple controls in containers",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Container(
            title="Container with wrapped controls",
            components=[
                vm.Graph(
                    title="Scatter chart",
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", custom_data=["species"]
                    ),
                ),
            ],
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.Checklist(value=["setosa"], title="Species"),
                ),
                vm.Filter(
                    column="petal_width",
                    selector=vm.RangeSlider(),
                ),
                vm.Filter(
                    column="sepal_length",
                    selector=vm.RangeSlider(),
                ),
            ],
        ),
        vm.Container(
            title="Container title",
            components=[
                vm.Graph(
                    title="Bar chart",
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species"),
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page1, page2, page3, page4, page5, page6, page7, page8, page9])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
