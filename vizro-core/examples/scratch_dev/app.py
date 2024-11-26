"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder_2007 = px.data.gapminder().query("year == 2007")

page = vm.Page(
    title="Tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab I",
                    components=[
                        vm.Graph(
                            title="Graph I",
                            figure=px.bar(
                                gapminder_2007,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            title="Graph II",
                            figure=px.box(
                                gapminder_2007,
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
                            title="Graph III",
                            figure=px.scatter(
                                gapminder_2007,
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

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
