"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_data_table

df = px.data.gapminder()

single_container_default_layout = vm.Page(
    title="Single Container - default layout",
    components=[
        vm.Container(
            title="Container 1",
            components=[
                vm.Graph(
                    id="graph_1",
                    figure=px.line(
                        df,
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
                    figure=px.scatter(
                        df,
                        title="Graph_2",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    id="graph_3",
                    figure=px.box(
                        df,
                        title="Graph_3",
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(function=export_data()),
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
            ],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        ),
        vm.Filter(column="continent"),
    ],
)


multiple_containers_custom_layout = vm.Page(
    title="Multiple Containers - custom layout",
    components=[
        vm.Container(
            title="Container 2",
            layout=vm.Layout(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    id="graph_11",
                    figure=px.line(
                        df,
                        title="Graph_11",
                        x="year",
                        y="lifeExp",
                        color="continent",
                        line_group="country",
                        hover_name="country",
                    ),
                ),
                vm.Graph(
                    id="graph_12",
                    figure=px.scatter(
                        df,
                        title="Graph_12",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
        ),
        vm.Container(
            title="Container 3",
            layout=vm.Layout(grid=[[0, 1]], row_min_height="300px"),
            components=[
                vm.Graph(
                    id="graph_13",
                    figure=px.box(
                        df,
                        title="Graph_13",
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(function=export_data()),
                    ],
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)

multiple_containers_nested = vm.Page(
    id="page_6",
    title="Multiple Containers - Nested",
    layout=vm.Layout(
        grid=[
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ],
        row_min_height="500px",
    ),
    components=[
        vm.Container(
            title="Container 4",
            layout=vm.Layout(grid=[[0, 1], [0, 1]]),
            components=[
                vm.Container(
                    title="Sub-Container 1",
                    layout=vm.Layout(
                        grid=[
                            [0, 0, 1, 1],
                            [0, 0, 1, 1],
                            [2, 2, 3, 3],
                            [2, 2, 3, 3],
                        ]
                    ),
                    components=[
                        vm.Graph(
                            id="graph_1rn",
                            figure=px.line(
                                df,
                                title="Graph_1",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                        vm.Graph(
                            id="graph_2rn",
                            figure=px.scatter(
                                df,
                                title="Graph_2",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_3rn",
                            figure=px.box(
                                df,
                                title="Graph_3",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_2rnn",
                            figure=px.scatter(
                                df,
                                title="Graph_2",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Container 5",
                    components=[
                        vm.Graph(
                            id="graph_6rn",
                            figure=px.line(
                                df,
                                title="Graph_6",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        )
                    ],
                ),
            ],
        ),
        vm.Container(
            title="Container 6",
            components=[
                vm.Graph(
                    id="graph_6rnn",
                    figure=px.line(
                        df,
                        title="Graph_6",
                        x="year",
                        y="lifeExp",
                        color="continent",
                        line_group="country",
                        hover_name="country",
                    ),
                )
            ],
        ),
    ],
)


graph_and_container = vm.Page(
    title="Graph and Container",
    components=[
        vm.Graph(
            figure=px.line(
                df,
                title="Graph Standalone",
                x="year",
                y="lifeExp",
                color="continent",
                line_group="country",
                hover_name="country",
            ),
        ),
        vm.Container(
            title="Container Standalone",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        title="Graph_2",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.box(
                        df,
                        title="Graph_3",
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="continent")],
)

table_and_container = vm.Page(
    title="Table and Container",
    components=[
        vm.Container(
            title="Container w/ Table",
            components=[
                vm.Table(title="Table Title", figure=dash_data_table(
                    id="dash_data_table_country",
                    data_frame=df,
                    page_size=30,
                ))
            ],
        ),
        vm.Container(
            title="Another Container",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        title="Graph_2",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="continent")],
)


dashboard = vm.Dashboard(
    pages=[
        single_container_default_layout,
        multiple_containers_custom_layout,
        multiple_containers_nested,
        graph_and_container,
        table_and_container,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
