"""Scratch demo app."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

iris = px.data.iris()


page_1 = vm.Page(
    title="Action Logs 1",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
