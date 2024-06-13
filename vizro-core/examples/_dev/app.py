"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

NUMBER_OF_COMPONENTS = 64


def squared_layout(N):
    import math

    size = math.ceil(math.sqrt(N))
    layout = [[(i * size + j) if (i * size + j) < N else -1 for j in range(size)] for i in range(size)]
    return layout


page_one = vm.Page(
    title="Page 1",
    layout=vm.Layout(grid=squared_layout(NUMBER_OF_COMPONENTS), col_gap="0px"),
    components=[
        vm.Graph(id=f"{i}_graph", figure=px.box(px.data.gapminder(), x="continent", y="lifeExp", title=f"Graph {i}"))
        for i in range(NUMBER_OF_COMPONENTS)
    ],
    controls=[vm.Filter(column="continent")],
)

page_two = vm.Page(
    title="Page 2",
    layout=vm.Layout(grid=[[0, 1], [2, 2]]),
    components=[
        vm.Table(title="Data Table", figure=dash_data_table(data_frame=px.data.gapminder())),
        vm.AgGrid(title="AG Grid", figure=dash_ag_grid(data_frame=px.data.gapminder())),
        vm.Graph(figure=px.box(px.data.gapminder(), x="continent", y="lifeExp", title="Graph")),
    ],
    controls=[vm.Filter(column="continent")],
)
dashboard = vm.Dashboard(
    pages=[page_one, page_two],
    # theme="vizro_light"
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
