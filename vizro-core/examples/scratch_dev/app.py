import vizro.plotly.express as px

import vizro.models as vm
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Collapse container",
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
            ],
            collapse=True,
            variant="outlined",
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
