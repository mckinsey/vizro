"""Development playground exploring markdown variations using built-in Vizro models."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder_2007 = px.data.gapminder().query("year == 2007")

page = vm.Page(
    title="Container title in Tabs",
    components=[
        vm.Tabs(
            title="Tabs Title",
            tabs=[
                vm.Container(
                    title="Tab I",
                    components=[
                        vm.Container(
                            title="Inner container I",
                            components=[
                                vm.Graph(
                                    title="Graph 1",
                                    figure=px.bar(
                                        gapminder_2007,
                                        x="continent",
                                        y="lifeExp",
                                        color="continent",
                                    ),
                                )
                            ],
                            variant="filled",
                        ),
                        vm.Container(
                            title="Inner container II",
                            components=[
                                vm.Graph(
                                    title="Graph 2",
                                    figure=px.box(
                                        gapminder_2007,
                                        x="continent",
                                        y="lifeExp",
                                        color="continent",
                                    ),
                                ),
                            ],
                            collapsed=False,
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 1]]),
                ),
                vm.Container(
                    title="Tab II",
                    components=[
                        vm.Graph(
                            title="Graph 3",
                            figure=px.scatter(
                                gapminder_2007,
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            title="Graph 2",
                            figure=px.box(
                                gapminder_2007,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Container(
                            title="Inner container III",
                            components=[
                                vm.Card(
                                    text="""
                                    #### Africa
                                    Africa, a diverse and expansive continent, faces both challenges and progress in
                                    its socioeconomic landscape. In 2007, Africa's GDP per cap was approximately $3,000.
                                    """
                                ),
                                vm.Card(
                                    text="""
                                    #### Asia
                                    Asia holds a central role in the global economy. It's growth in GDP per capita to
                                    $12,000 in 2007 and population has been significant, outpacing many other
                                    continents.
                                """
                                ),
                                vm.Card(
                                    text="""
                                    #### Europe
                                    Europe boasts a strong and thriving economy. In 2007, it exhibited the
                                    second-highest GDP per capita of $25,000 among continents.
                                """
                                ),
                            ],
                            layout=vm.Grid(grid=[[0, 1, 2]]),
                            variant="filled",
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 1], [0, 1], [2, 2]]),
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="continent")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
