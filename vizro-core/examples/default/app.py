"""Example to show dashboard configuration."""
import os

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

df_gapminder = px.data.gapminder()

page = vm.Page(
    title="Testing out tabs",
    components=[
        vm.Tabs(
            subpages=[
                vm.SubPage(
                    id="tab-1",
                    title="Tab I Title",
                    components=[
                        vm.Graph(
                            id="graph-1",
                            figure=px.line(
                                df_gapminder,
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                        vm.Graph(
                            id="graph-2",
                            figure=px.scatter(
                                df_gapminder.query("year==2007"),
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                                title="Comparison of gdpPercap and lifeExp",
                            ),
                        ),
                        vm.Graph(
                            id="graph-3",
                            figure=px.box(
                                df_gapminder,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                                title="Distribution per continent",
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
                vm.SubPage(
                    id="tab-2",
                    title="Tab II",
                    components=[
                        vm.Graph(
                            id="graph-4",
                            figure=px.scatter(
                                df_gapminder.query("year==2007"),
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                                title="Comparison of gdpPercap and lifeExp",
                            ),
                        ),
                        vm.Graph(
                            id="graph-5",
                            figure=px.box(
                                df_gapminder,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                                title="Distribution per continent",
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
            targets=["graph-1.y", "graph-2.y", "graph-3.y", "graph-4.y", "graph-5.y"],
            selector=vm.RadioItems(options=["lifeExp", "pop", "gdpPercap"], title="Select variable"),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()
