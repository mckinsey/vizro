import vizro.plotly.express as px
from typing import Literal
import vizro.models as vm
from vizro import Vizro
from dash import html

iris = px.data.iris()


class FlexContainer(vm.Container):
    """FlexContainer for testing."""

    type: Literal["flex_container"] = "flex_container"

    def build(self):
        """Returns custom flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )


vm.Page.add_type("components", FlexContainer)

page_flex = vm.Page(
    title="Flex - Collapse",
    controls=[vm.Filter(column="species")],
    components=[
        FlexContainer(
            title="Flex-Container",
            components=[
                vm.Container(
                    title="Container title 1",
                    collapse=False,
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                    ],
                    layout=vm.Layout(grid=[[0, 1]]),
                    variant="outlined",
                ),
                vm.Container(
                    title="Container title 2",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                    ],
                    collapse=True,
                    variant="outlined",
                    layout=vm.Layout(grid=[[0, 1]]),
                ),
            ],
        )
    ],
)

page_grid = vm.Page(
    title="Grid - Collapse",
    controls=[vm.Filter(column="species")],
    components=[
        vm.Container(
            title="Container title 1",
            collapse=False,
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
            ],
            layout=vm.Layout(grid=[[0, 1]]),
            variant="outlined",
        ),
        vm.Container(
            title="Container title 2",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
            ],
            collapse=True,
            variant="outlined",
            layout=vm.Layout(grid=[[0, 1]]),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_grid, page_flex])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
