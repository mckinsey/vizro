import vizro.plotly.express as px

import vizro.models as vm
from vizro import Vizro
from components import CollapsibleContainer, FlexContainer

vm.Page.add_type("components", FlexContainer)
vm.Page.add_type("components", CollapsibleContainer)

FlexContainer.add_type("components", CollapsibleContainer)

iris = px.data.iris()

page_1=vm.Page(
    title="Collapse containers with flex container",
    components=[
        FlexContainer(
            components=[
                CollapsibleContainer(
                    title="Collapsible container",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                        vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ],
                    layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 2, 2]]),
                    is_open=False,
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
    ]
)


page_2 = vm.Page(
    title="Collapsible containers inside grid layout",
    components=[
        CollapsibleContainer(
            title="Collapsible container",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 2, 2]]),
            is_open=False,
        ),
        CollapsibleContainer(
            title="Collapsible container 2",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.histogram(iris, x="sepal_width", color="species")),
            ],
            layout=vm.Layout(grid=[[0, 0, 0, 0], [1, 1, 1, 1]]),
        )
    ]
)


dashboard = vm.Dashboard(pages=[page_1, page_2])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
