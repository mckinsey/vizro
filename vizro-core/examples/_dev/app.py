"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()
iris = px.data.iris()

containers = vm.Page(
    title="Containers",
    components=[
        vm.Container(
            title="Container I",
            layout=vm.Layout(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris, x="sepal_length", y="petal_width", color="species", title="Container I - Scatter"
                    )
                ),
                vm.Graph(
                    figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species", title="Container I - Bar")
                ),
            ],
        ),
        vm.Container(
            title="Container II",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        marginal_y="violin",
                        marginal_x="box",
                        title="Container II - Scatter",
                    )
                ),
            ],
        ),
    ],
)

single_tabs = vm.Page(
    title="Single Tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I",
                    components=[
                        vm.Graph(
                            id="graph_1",
                            figure=px.line(
                                gapminder,
                                title="Graph_1",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                        vm.Graph(
                            id="graph_2",
                            figure=px.box(
                                gapminder,
                                title="Graph_3",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab II",
                    components=[
                        vm.Graph(
                            id="graph_3",
                            figure=px.scatter(
                                gapminder,
                                title="Graph_4",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_4",
                            figure=px.box(
                                gapminder,
                                title="Graph_5",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[
                "graph_1.y",
                "graph_2.y",
                "graph_3.y",
                "graph_4.y",
            ],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        ),
        vm.Filter(column="continent"),
    ],
)


single_tabs_action = vm.Page(
    title="Single Tabs - with action",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I Table",
                    components=[
                        vm.Table(
                            figure=dash_data_table(
                                id="dash_datatable-1",
                                data_frame=gapminder,
                            ),
                        ),
                        vm.Button(
                            text="Export data",
                            actions=[
                                vm.Action(function=export_data()),
                            ],
                        ),
                    ],
                )
            ]
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)

tabs_and_component = vm.Page(
    title="Tabs and Component",
    components=[
        vm.Graph(
            figure=px.box(
                gapminder,
                title="Graph_5",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I Table",
                    components=[
                        vm.Table(
                            figure=dash_data_table(
                                id="dash_datatable-1",
                                data_frame=gapminder,
                            ),
                        ),
                    ],
                )
            ]
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)


multiple_tabs = vm.Page(
    title="Multiple Tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab 1 container 1",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                gapminder,
                                title="Graph_44",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab 1 container 2",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                gapminder,
                                title="Graph_441",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab 2 container",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                gapminder,
                                title="Graph_45",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab 2 container 2",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                gapminder,
                                title="Graph_451",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


dashboard = vm.Dashboard(
    title="Dashboard Title", pages=[containers, single_tabs, single_tabs_action, tabs_and_component, multiple_tabs]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
