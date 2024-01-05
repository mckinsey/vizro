"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

df = px.data.gapminder()


page_variable = vm.Page(
    title="Variable Analysis",
    description="Analyzing population, GDP per capita and life expectancy on country and continent level",
    components=[
        vm.Card(
            text="""
                ### Overview
                The world map provides initial insights into the variations of metrics across countries and
                continents. Click on Play to see the animation and explore the development over time.

                #### Observation
                A global trend of increasing life expectancy emerges, with some exceptions in specific African
                countries. Additionally, despite similar population growth rates across continents, the overall
                global population continues to expand, with India and China leading the way.  Meanwhile, GDP per
                capita experiences growth in most regions.

            """
        ),
        vm.Graph(
            id="variable_map",
            figure=px.choropleth(
                df,
                locations="iso_alpha",
                color="lifeExp",
                hover_name="country",
                animation_frame="year",
                labels={
                    "year": "year",
                    "lifeExp": "Life expectancy",
                    "pop": "Population",
                    "gdpPercap": "GDP per capita",
                },
                title="Global development over time",
            ),
        ),
        vm.Card(
            text="""
                ### Distribution
                The boxplot illustrates the distribution of each metric across continents, facilitating comparisons
                of life expectancy, GDP per capita, and population statistics.

                Observations reveal that Europe and Oceania have the highest life expectancy and GDP per capita,
                likely influenced by their smaller population growth. Additionally, Asia and America exhibit
                notable GDP per capita outliers, indicating variations among countries within these continents or
                large growth over the observed years.
            """
        ),
        vm.Graph(
            id="variable_boxplot",
            figure=px.box(
                df,
                x="continent",
                y="lifeExp",
                color="continent",
                labels={
                    "year": "year",
                    "lifeExp": "Life expectancy",
                    "pop": "Population",
                    "gdpPercap": "GDP per capita",
                    "continent": "Continent",
                },
                title="Distribution per continent",
                color_discrete_map={
                    "Africa": "#00b4ff",
                    "Americas": "#ff9222",
                    "Asia": "#3949ab",
                    "Europe": "#ff5267",
                    "Oceania": "#08bdba",
                },
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["variable_map.color", "variable_boxplot.y"],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        )
    ],
)


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
        ]
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


dashboard = vm.Dashboard(
    pages=[
        page_variable,
        single_container_default_layout,
        multiple_containers_custom_layout,
        multiple_containers_nested,
    ]
)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
