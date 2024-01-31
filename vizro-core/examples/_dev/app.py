"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

child_container_one = vm.Container(
    title="Container I",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            figure=px.line(
                gapminder,
                title="Graph 1 - Container I",
                x="year",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.scatter(
                gapminder,
                title="Graph 2 - Container I",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                gapminder,
                title="Graph 3 - Container I",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
    ],
)

child_container_two = vm.Container(
    title="Container II",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Graph(
            figure=px.line(
                gapminder,
                title="Graph 4 - Container II",
                x="year",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.scatter(
                gapminder,
                title="Graph 5 - Container II",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)

page = vm.Page(
    title="Nested Containers",
    components=[
        vm.Container(
            title="Parent Container",
            layout=vm.Layout(grid=[[0, 1]], col_gap="80px"),
            components=[child_container_one, child_container_two],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
