"""Example to show dashboard configuration."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.figures import kpi_card
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

data = pd.DataFrame(
    {
        "Column 1": [1, 2, 3, 4, 5, 6],
        "Column 2": ["A", "B", "C", "VeryLongStringInputCell_VeryLongStringInputCell", "D", "E"],
        "Column 3": [10.5, 20.1, 30.2, 40.3, 50.4, 60.5],
    }
)


def load_data():
    """Load data."""
    return data


data_manager["my_data"] = load_data


@capture("ag_grid")
def custom_dash_ag_grid(data_frame, **kwargs):
    """Custom AgGrid."""
    # print(f"dash_ag_grid -> len: {len(data_frame)}")
    return dash_ag_grid(data_frame, **kwargs)()


@capture("table")
def custom_dash_data_table(data_frame, **kwargs):
    """Custom DataTable."""
    # print(f"dash_data_table -> len: {len(data_frame)}")
    return dash_data_table(data_frame, **kwargs)()


@capture("graph")
def custom_px_scatter(data_frame, **kwargs):
    """Custom Scatter plot."""
    # print(f"graph -> len: {len(data_frame)}")
    return px.scatter(data_frame, **kwargs)


@capture("figure")
def custom_kpi_card(data_frame, **kwargs):
    """Custom KPI card."""
    # print(f"kpi_card -> len: {len(data_frame)}")
    return kpi_card(data_frame, **kwargs)()


page_grid = vm.Page(
    title="Example Page",
    layout=vm.Layout(
        grid=[
            [0, 1],
            [2, 3],
        ]
    ),
    components=[
        vm.AgGrid(
            id="outer_ag_grid_id",
            figure=custom_dash_ag_grid(
                id="inner_ag_grid_id",
                data_frame="my_data",
                columnDefs=[{"field": col, "checkboxSelection": True, "filter": True} for col in data.columns],
                columnSize="autoSize",
                defaultColDef={"resizable": True},
                persistence=True,
                persistence_type="local",
                persisted_props=["selectedRows", "filterModel"],
                dashGridOptions={
                    "rowSelection": "multiple",
                    "suppressRowClickSelection": True,
                    # Turn pagination on to see results:
                    # "pagination": True,
                    # "paginationPageSize": 3,
                },
            ),
            actions=[
                vm.Action(
                    function=filter_interaction(targets=["graph_id"]),
                )
            ],
        ),
        vm.Table(
            id="outer_table_id",
            figure=custom_dash_data_table(
                id="inner_table_id",
                data_frame="my_data",
                row_selectable="multi",
                filter_action="native",
                persistence=True,
                persistence_type="local",
                # Turn pagination on to see results:
                # page_action="native",
                # page_size=3,
            ),
        ),
        vm.Graph(
            id="graph_id",
            figure=custom_px_scatter(data_frame="my_data", x="Column 1", y="Column 3"),
        ),
        vm.Figure(
            id="figure_id",
            figure=custom_kpi_card(data_frame="my_data", value_column="Column 1"),
        ),
    ],
    controls=[vm.Filter(column="Column 1", selector=vm.RangeSlider(step=1))],
)

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Page_1",
            components=[vm.Card(text="Dummy page just for testing")],
        ),
        page_grid,
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
