"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page = vm.Page(
    title="Page Two",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(iris, title="My scatter chart", x="sepal_length", y="petal_width", color="species"),
        )
    ],
    controls=[
        vm.ControlGroup(
            title="Control group title",
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(variant="filled")),
                vm.Filter(column="sepal_length", selector=vm.Slider()),
            ],
        ),
        vm.ControlGroup(
            id="ctl2",
            title="Parameters",
            controls=[
                vm.Parameter(
                    targets=["scatter_chart.title"],
                    selector=vm.Dropdown(
                        title="Choose title",
                        options=["My scatter chart", "A better title!", "Another title..."],
                        multi=False,
                    ),
                ),
            ],
        ),
        vm.Filter(column="sepal_length", selector=vm.Slider()),
    ],
)

page_2 = vm.Page(
    title="ControlGroup in Container",
    components=[
        vm.Container(
            title="Bar chart container",
            components=[
                vm.Graph(
                    id="bar_chart",
                    figure=px.bar(
                        iris,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                    ),
                ),
            ],
            controls=[
                vm.ControlGroup(
                    title="Control group in container",
                    controls=[
                        vm.Parameter(
                            targets=["bar_chart.color_discrete_map.virginica"],
                            selector=vm.Dropdown(
                                options=["#ff5267", "#3949ab"],
                                multi=False,
                                value="#3949ab",
                            ),
                        ),
                        vm.Filter(column="species", selector=vm.Dropdown(variant="filled")),
                    ],
                ),
                vm.ControlGroup(
                    title="Control group in container",
                    controls=[
                        vm.Filter(column="sepal_length"),
                    ],
                ),
            ],
        ),
        vm.Container(
            title="Container without controls",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        iris, title="My scatter chart", x="sepal_length", y="petal_width", color="species"
                    ),
                )
            ],
        ),
    ],
    layout=vm.Grid(grid=[[0, 1]]),
)


dashboard = vm.Dashboard(
    pages=[page, page_2],
    title="QB",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
