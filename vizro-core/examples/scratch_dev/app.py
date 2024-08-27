"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

# NUMBER_OF_COMPONENTS = 4
NUMBER_OF_COMPONENTS = 64


def squared_layout(N):
    """Util function."""
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
        vm.Table(
            id="P2_table", title="Data Table", figure=dash_data_table(id="P2_UL_table", data_frame=px.data.gapminder())
        ),
        vm.AgGrid(
            id="P2_aggrid", title="AG Grid", figure=dash_ag_grid(id="P2_UL_aggrid", data_frame=px.data.gapminder())
        ),
        vm.Graph(
            id="P2_graph",
            figure=px.box(px.data.gapminder(), x="continent", y="lifeExp", title="Graph", animation_frame="year"),
        ),
    ],
    controls=[vm.Filter(column="continent")],
)
dashboard = vm.Dashboard(pages=[page_one, page_two], theme="vizro_light")


if __name__ == "__main__":
    Vizro(suppress_callback_exceptions=True).build(dashboard).run()
