"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.gapminder()
nested_container_one = vm.Container(
    title="Nested Container I",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Graph(
            figure=px.line(
                df,
                title="Graph 1 - Nested Container I",
                x="year",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.scatter(
                df,
                title="Graph 2 - Nested Container I",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                df,
                title="Graph 3 - Nested Container I",
                x="continent",
                y="lifeExp",
                color="continent",
            ),
        ),
    ],
)
nested_container_two = vm.Container(
    title="Nested Container II",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Graph(
            figure=px.line(
                df,
                title="Graph 4 - Nested Container II",
                x="year",
                y="lifeExp",
                color="continent",
            ),
        ),
        vm.Graph(
            figure=px.scatter(
                df,
                title="Graph 5 - Nested Container II",
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
            title="Container Title",
            layout=vm.Layout(grid=[[0, 1]], col_gap="80px"),
            components=[nested_container_one, nested_container_two],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
