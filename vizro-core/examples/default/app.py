"""Example to show dashboard configuration."""
import os

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df_gapminder = px.data.gapminder()

page = vm.Page(
    title="Testing out tabs",
    components=[
        vm.Tabs(
            title="Global Tabs Title",
            tabs=[
                vm.Tab(
                    label="Tab I Label",
                    title="Tab I Title",
                    components=[
                        vm.Graph(
                            id="variable_map",
                            figure=px.scatter(
                                df_gapminder.query("year==2007"),
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                                hover_name="country",
                                log_x=True,
                                size_max=60,
                                title="Comparison of gdpPercap and lifeExp",
                            ),
                        )
                    ],
                ),
                vm.Tab(
                    label="Tab II Label",
                    title="Tab II Title",
                    components=[
                        vm.Graph(
                            id="variable_boxplot",
                            figure=px.box(
                                df_gapminder,
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
                ),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["variable_map.y", "variable_boxplot.y"],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()
