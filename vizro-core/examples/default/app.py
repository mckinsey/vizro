"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

df_gapminder = px.data.gapminder()


single_container_default_layout = vm.Page(
    title="Single Container - default layout",
    components=[
        vm.Container(
            id="container-1",
            title="Container I",
            components=[
                vm.Graph(
                    id="graph_1",
                    figure=px.line(
                        df_gapminder,
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
                        df_gapminder,
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
                        df_gapminder,
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
            id="cont_1",
            title="Container I",
            layout=vm.Layout(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    id="graph_11",
                    figure=px.line(
                        df_gapminder,
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
                        df_gapminder,
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
            id="cont_2",
            title="Container II",
            layout=vm.Layout(grid=[[0, 1]], row_min_height="300px"),
            components=[
                vm.Graph(
                    id="graph_13",
                    figure=px.box(
                        df_gapminder,
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
        ]
    ),
    components=[
        vm.Container(
            layout=vm.Layout(grid=[[0, 1], [0, 1]]),
            components=[
                vm.Container(
                    title="Another container",
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
                                df_gapminder,
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
                                df_gapminder,
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
                                df_gapminder,
                                title="Graph_3",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_2rnn",
                            figure=px.scatter(
                                df_gapminder,
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
                    components=[
                        vm.Graph(
                            id="graph_6rn",
                            figure=px.line(
                                df_gapminder,
                                title="Graph_6",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        )
                    ]
                ),
            ],
        ),
        vm.Container(
            title="Second container",
            components=[
                vm.Graph(
                    id="graph_6rnn",
                    figure=px.line(
                        df_gapminder,
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


dashboard = vm.Dashboard(
    pages=[single_container_default_layout, multiple_containers_custom_layout, multiple_containers_nested]
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
