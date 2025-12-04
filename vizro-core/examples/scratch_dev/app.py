import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()
iris = px.data.iris()
tips = px.data.tips()

filtered_gapminder = gapminder[(gapminder["continent"] == "Europe") & (gapminder["year"] == 2007)]

page_grid_0 = vm.Page(
    title="Grid",
    layout=vm.Grid(
        grid=[[0, 1], [2, 2]],
        row_min_height="1000px",
    ),
    components=[
        vm.Container(
            title="",
            components=[
                vm.AgGrid(figure=dash_ag_grid(data_frame=filtered_gapminder)),
            ],
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="petal_length"), title="Title"),
        vm.AgGrid(figure=dash_ag_grid(data_frame=iris)),
    ],
)


page_grid_1 = vm.Page(
    title="Grid - in column",
    layout=vm.Grid(
        grid=[[0], [1], [2], [3], [4]],
        row_min_height="1000px",
    ),
    components=[
        vm.Button(text="Button"),
        vm.Button(text="Button"),
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Button(text="Button"),
        vm.Button(text="Button"),
    ],
)


page_grid_2 = vm.Page(
    title="Grid - in row",
    layout=vm.Grid(
        grid=[[0, 1, 2, 3, 4]],
        col_min_width="1000px",
    ),
    components=[
        vm.Button(text="Button"),
        vm.Button(text="Button"),
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Button(text="Button"),
        vm.Button(text="Button"),
    ],
)

page_flex_0 = vm.Page(
    title="Flex",
    layout=vm.Flex(),
    components=[
        vm.Container(
            title="",
            components=[
                vm.AgGrid(figure=dash_ag_grid(data_frame=filtered_gapminder)),
            ],
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="petal_length"), title="Title"),
        vm.AgGrid(figure=dash_ag_grid(data_frame=iris)),
    ],
)


page_flex_1 = vm.Page(
    title="Flex - in column",
    layout=vm.Flex(direction="column"),
    components=[
        vm.Button(text="Button"),
        vm.Button(text="Button"),
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Button(text="Button"),
        vm.Button(text="Button"),
    ],
)

page_flex_2 = vm.Page(
    title="Flex - in row",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(text="Button"),
        vm.Button(text="Button"),
        vm.AgGrid(figure=dash_ag_grid(tips)),
        vm.Button(text="Button"),
        vm.Button(text="Button"),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_grid_0,
        page_grid_1,
        page_grid_2,
        page_flex_0,
        page_flex_1,
        page_flex_2,
    ],
    title="Test out Flex/Grid",
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
