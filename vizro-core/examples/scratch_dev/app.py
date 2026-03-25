"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_1 = vm.Page(
    title="Page with ControlGroup",
    components=[
        vm.Graph(
            id="scatter_chart",
            title="My scatter chart",
            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
        )
    ],
    controls=[
        vm.ControlGroup(
            title="Control group title",
            controls=[
                vm.Filter(
                    column="species", selector=vm.Dropdown(title="Species", variant="filled", description="test")
                ),
                vm.Filter(column="sepal_length", selector=vm.Slider()),
            ],
            description="test",
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
                        description=vm.Tooltip(icon="Shopping Cart", text="test"),
                    ),
                ),
            ],
            description=vm.Tooltip(icon="Favorite", text="test"),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.Slider(title="Sepal length", description=vm.Tooltip(icon="Dashboard", text="test")),
        ),
    ],
)


page_2 = vm.Page(
    title="Regular page",
    components=[
        vm.Graph(
            title="My scatter chart",
            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
        )
    ],
    controls=[vm.Filter(column="sepal_length"), vm.Filter(column="species")],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
