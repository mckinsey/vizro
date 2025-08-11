# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import collapse_expand_containers

iris = px.data.iris()

page_5 = vm.Page(
    title="Page with containers",
    components=[
        vm.Button(
            text="Collapse all containers",
            actions=[collapse_expand_containers(collapse=["container3", "container4"])],
        ),
        vm.Button(
            text="Expand all containers",
            actions=[collapse_expand_containers(expand=["container1", "container2"])],
        ),
        vm.Container(
            title="",
            layout=vm.Flex(),
            components=[
                vm.Container(
                    id="container1",
                    title="Container 1",
                    components=[vm.Graph(figure=px.bar(iris, x="species", y="petal_length"))],
                    collapsed=True,
                ),
                vm.Container(
                    id="container2",
                    title="Container 2",
                    components=[vm.Graph(figure=px.bar(iris, x="species", y="petal_length"))],
                    collapsed=True,
                ),
                vm.Container(
                    id="container3",
                    title="Container 3",
                    components=[vm.Graph(figure=px.bar(iris, x="species", y="petal_length"))],
                    collapsed=False,
                ),
                vm.Container(
                    id="container4",
                    title="Container 4",
                    components=[vm.Graph(figure=px.bar(iris, x="species", y="petal_length"))],
                    collapsed=False,
                ),
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="species",
        )
    ],
    layout=vm.Grid(
        grid=[
            [0, 1, -1, -1, -1],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_5])

if __name__ == "__main__":
    Vizro().build(dashboard).run(
        debug=True,
        use_reloader=False,
    )
