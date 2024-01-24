"""Rough example used by developers."""
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.gapminder()

page = vm.Page(
    title="Nested Containers",
    layout=vm.Layout(
        grid=[[0, 1], [0, 1]],
        row_min_height="400px",
    ),
    components=[
        vm.Container(
            title="Container",
            layout=vm.Layout(grid=[[0, 1], [0, 1]]),
            components=[
                vm.Container(
                    title="Nested Container",
                    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
                    components=[
                        vm.Graph(
                            figure=px.line(
                                df,
                                title="Graph 1 - Nested Container",
                                x="year",
                                y="lifeExp",
                                color="continent",
                                line_group="country",
                                hover_name="country",
                            ),
                        ),
                        vm.Graph(
                            figure=px.scatter(
                                df,
                                title="Graph 2 - Nested Container",
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                        vm.Graph(
                            figure=px.box(
                                df,
                                title="Graph 3 - Nested Container",
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Graph(
                    figure=px.line(
                        df,
                        title="Graph 4 - Container",
                        x="year",
                        y="lifeExp",
                        color="continent",
                        line_group="country",
                        hover_name="country",
                    ),
                ),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
