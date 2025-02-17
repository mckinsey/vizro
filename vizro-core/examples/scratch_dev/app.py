"""Test app"""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

page = vm.Page(
    title="Page with subsections",
    layout=vm.Layout(grid=[[0, 3, 3, 3, 4, 4], [1, 3, 3, 3, 4, 4], [2, 3, 3, 3, 4, 4]]),
    components=[
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Card(text="""Hello, this is a card with a [link](https://www.google.com)"""),
        vm.Container(
            title="Container I",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
            background=True,
        ),
        vm.Container(
            title="Container II",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
            background=True,
        ),
    ],
)

page_two = vm.Page(
    title="Container",
    components=[
        vm.Container(
            title="Container III",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
