"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_data_table

gapminder = px.data.gapminder()

single_tabs = vm.Page(
    title="Single Tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I",
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
                            id="bar_relation_2007",
                            figure=px.box(
                                gapminder,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                                custom_data=["continent"],
                            ),
                            actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab II",
                    components=[
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
                        vm.Graph(
                            id="scatter_relation_2007",
                            figure=px.scatter(
                                gapminder,
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
    controls=[
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


tabs_with_nested_containers = vm.Page(
    title="Tabs with nested containers",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab 1",
                    components=[
                        vm.Container(
                            title="Nested Container Title",
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
            ],
        ),
        vm.Container(
            title="Container Title",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        gapminder,
                        title="Graph_45",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    )
                )
            ],
        ),
    ],
)

tabs_without_charts = vm.Page(
    title="Tabs without Graphs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I",
                    components=[
                        vm.Table(
                            figure=dash_data_table(
                                id="dash_datatable-single",
                                data_frame=gapminder,
                            ),
                        ),
                        vm.Graph(
                            figure=px.box(
                                gapminder,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                                custom_data=["continent"],
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab II",
                    components=[
                        vm.Card(
                            text="""
                                ![](assets/images/icons/collections.svg#icon-top)

                                ### Continent Summary

                                Summarizing the main findings for each continent.
                            """,
                        ),
                        vm.Graph(
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
        vm.Filter(column="continent"),
    ],
)

dashboard = vm.Dashboard(
    title="Dashboard Title",
    pages=[
        single_tabs,
        single_tabs_action,
        tabs_and_component,
        multiple_tabs,
        tabs_with_nested_containers,
        tabs_without_charts,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
