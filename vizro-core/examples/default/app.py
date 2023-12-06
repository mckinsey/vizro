"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_data_table

df_gapminder = px.data.gapminder()

page = vm.Page(
    # title="Testing out tabs: [0, [1, 2 ,3, B], [4, 5, [6, 7], [8]]]",
    title="Regular tabs - default layout",
    components=[
        # vm.Table(
        #     id="table-0",
        #     figure=dash_data_table(
        #         id="dash_datatable-0",
        #         data_frame=df_gapminder,
        #     ),
        #     actions=[
        #         vm.Action(
        #             function=filter_interaction(
        #                 targets=["graph_1", "graph_2", "graph_3", "graph_4", "graph_5", "graph_6", "graph_7", "graph_8"]
        #             )
        #         ),
        #     ],
        # ),
        vm.Tabs(
            id="first_tab",
            tabs=[
                vm.Container(
                    id="tab-1",
                    title="Tab I Title",
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
                vm.Container(
                    id="tab-2",
                    title="Tab II",
                    components=[
                        vm.Graph(
                            id="graph_4",
                            figure=px.scatter(
                                df_gapminder,
                                title="Graph_4",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_5",
                            figure=px.box(
                                df_gapminder,
                                title="Graph_5",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_6",
                            figure=px.line(
                                df_gapminder,
                                title="Graph_6",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
    controls=[
        # TODO: Fix issue of graphs only being updated if they are target of controls
        # e.g. if you don't add the parameter below, all of the charts will not get loaded
        # probably need to implement some logic for an on_tab_load action
        vm.Parameter(
            targets=[
                "graph_1.y",
                "graph_2.y",
                "graph_3.y",
                "graph_4.y",
                "graph_5.y",
                "graph_6.y",
            ],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        ),
        vm.Filter(column="continent"),
    ],
)
page_2 = vm.Page(
    title="Containers page",
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
page_3 = vm.Page(
    title="Third page",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    id="container_table",
                    title="Tab I Table",
                    components=[
                        vm.Table(
                            id="table-1",
                            figure=dash_data_table(
                                id="dash_datatable-1",
                                data_frame=df_gapminder,
                            ),
                        ),
                    ],
                )
            ]
        ),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)

page_4 = vm.Page(
    id="page_4",
    title="Tabs",
    components=[
        vm.Tabs(
            id="page-4-tab1",
            tabs=[
                vm.Container(
                    title="Tab 1 container 1",
                    components=[
                        vm.Graph(
                            id="graph_44",
                            figure=px.scatter(
                                df_gapminder,
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
                            id="graph_441",
                            figure=px.scatter(
                                df_gapminder,
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
            id="page-4-tab2",
            tabs=[
                vm.Container(
                    title="Tab 2 container",
                    components=[
                        vm.Graph(
                            id="graph_45",
                            figure=px.scatter(
                                df_gapminder,
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
                            id="graph_451",
                            figure=px.scatter(
                                df_gapminder,
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
page_5 = vm.Page(
    # title="Testing out tabs: [0, [1, 2 ,3, B], [4, 5, [6, 7], [8]]]",
    title="Regular tabs - with layout",
    components=[
        vm.Tabs(
            id="first-tabr",
            tabs=[
                vm.Container(
                    layout=vm.Layout(grid=[[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 2, 2], [1, 1, 2, 2], [3, -1, -1, -1]]),
                    id="tab-1r",
                    title="Tab I Title",
                    components=[
                        vm.Graph(
                            id="graph_1r",
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
                            id="graph_2r",
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
                            id="graph_3r",
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
                vm.Container(
                    id="tab-2r",
                    title="Tab II",
                    layout=vm.Layout(
                        grid=[
                            [0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [1, 1, 2, 2],
                            [1, 1, 2, 2],
                        ]
                    ),
                    components=[
                        vm.Graph(
                            id="graph_4r",
                            figure=px.scatter(
                                df_gapminder,
                                title="Graph_4",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_5r",
                            figure=px.box(
                                df_gapminder,
                                title="Graph_5",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            id="graph_6r",
                            figure=px.line(
                                df_gapminder,
                                title="Graph_6",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

page_6 = vm.Page(
    id="page_6",
    title="Nested container",
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

dashboard = vm.Dashboard(pages=[page, page_5, page_2, page_3, page_4, page_6])

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
