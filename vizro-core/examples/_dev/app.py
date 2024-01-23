"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_data_table

df_gapminder = px.data.gapminder()


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
                            figure=px.box(
                                df_gapminder,
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
                                df_gapminder,
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
                                df_gapminder,
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
                                data_frame=df_gapminder,
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
                df_gapminder,
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
                                data_frame=df_gapminder,
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
            tabs=[
                vm.Container(
                    title="Tab 2 container",
                    components=[
                        vm.Graph(
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


dashboard = vm.Dashboard(
    title="Dashboard Title", pages=[single_tabs, single_tabs_action, tabs_and_component, multiple_tabs]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
