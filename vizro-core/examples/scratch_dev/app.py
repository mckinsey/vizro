import vizro.plotly.express as px

import vizro.models as vm
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Collapse container",
    components=[
        vm.Container(
            title="Container title",
            collapse=True,
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
            ]
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
