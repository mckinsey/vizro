"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from components import CollapsibleContainer, FlexContainer

vm.Page.add_type("components", FlexContainer)
FlexContainer.add_type("components", CollapsibleContainer)
vm.Page.add_type("components", CollapsibleContainer)

iris = px.data.iris()

page = vm.Page(
    title="Collapse containers with flex container",
    components=[
        FlexContainer(
            components=[
                CollapsibleContainer(
                    id="collapsible-container",
                    title="Collapsible container",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                    layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 2, 2]]),
                ),
                CollapsibleContainer(
                    title="Collapsible container 2",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                    ],
                    layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 1, 1]]),
                ),
            ]
        )
    ],
)


dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
