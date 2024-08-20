# custom graph/table/grid

"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.managers import data_manager
from vizro.models.types import capture


@capture("graph")
def custom_graph(data_frame, **kwargs):
    print(f"Graph len: {len(data_frame)}")
    return px.box(data_frame, **kwargs)


@capture("ag_grid")
def custom_ag_grid(data_frame, **kwargs):
    print(f"AG Grid len: {len(data_frame)}")
    return dash_ag_grid(data_frame, **kwargs)()


@capture("table")
def custom_table(data_frame, **kwargs):
    print(f"Table len: {len(data_frame)}")
    return dash_data_table(data_frame, **kwargs)()


def load_data():
    return px.data.gapminder()


data_manager["my_data"] = load_data


page_one = vm.Page(
    title="Graph / AG Grid",
    components=[
        vm.Graph(
            figure=custom_graph(
                data_frame="my_data",
                x="continent",
                y="lifeExp",
                color="continent",
                title="Graph",
            )
        ),
        vm.AgGrid(
            title="AgGrid",
            figure=custom_ag_grid(
                data_frame="my_data"
            )
        ),
        vm.Table(
            title="Table",
            figure=custom_table(
                data_frame="my_data"
            )
        ),
    ],
    controls=[
        vm.Filter(column="continent")
    ]
)

page_two = vm.Page(
    title="Page_2",
    components=[vm.Button()],
)


dashboard = vm.Dashboard(pages=[page_one, page_two])


if __name__ == "__main__":
    Vizro(suppress_callback_exceptions=True).build(dashboard).run()
