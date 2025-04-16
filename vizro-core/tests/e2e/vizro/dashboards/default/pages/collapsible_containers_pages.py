import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px

iris = px.data.iris()

collapsible_containers_grid = vm.Page(
    title=cnst.COLLAPSIBLE_CONTAINERS_GRID,
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Container(
            title="Initially collapsed container",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
            collapsed=True,
            variant="filled",
        ),
        vm.Container(
            title="Initially expanded container",
            components=[vm.Graph(figure=px.box(iris, x="species", y="sepal_length", color="species"))],
            collapsed=False,
        ),
    ],
)

collapsible_containers_flex = vm.Page(
    title=cnst.COLLAPSIBLE_CONTAINERS_FLEX,
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="Initially collapsed container",
            components=[vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"))],
            collapsed=True,
            variant="filled",
        ),
        vm.Container(
            title="Initially expanded container",
            components=[vm.Graph(figure=px.box(iris, x="species", y="sepal_length", color="species"))],
            collapsed=False,
        ),
    ],
)
