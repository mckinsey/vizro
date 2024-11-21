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
                            figure=px.bar(
                                gapminder_2007,
                                title="Graph 1",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            figure=px.box(
                                gapminder_2007,
                                title="Graph 2",
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
                            figure=px.scatter(
                                gapminder_2007,
                                title="Graph 3",
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
    controls=[vm.Filter(column="continent")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == '__main__':
    Vizro().build(dashboard).run()
