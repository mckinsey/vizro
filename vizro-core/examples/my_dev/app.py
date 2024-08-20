# custom graph/table/grid

"""Example to show dashboard configuration."""
import pandas as pd
import dash_ag_grid as dag


import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.managers import data_manager
from vizro.models.types import capture


@capture("ag_grid")
def custom_ag_grid(data_frame, **kwargs):
    print(f"AG Grid len: {len(data_frame)}")
    vizro_dash_ag_grid = dash_ag_grid(data_frame, **kwargs)
    return vizro_dash_ag_grid()


data = pd.DataFrame({
    'Column 1': [1, 2, 3, 4, 5, 6],
    'Column 2': ['A', 'B', 'C', 'VeryLongStringInputCell_VeryLongStringInputCell_VeryLongStringInputCell', 'D', 'E'],
    'Column 3': [10.5, 20.1, 30.2, 40.3, 50.4, 60.5],
})


def load_data():
    return data


data_manager["my_data"] = load_data


@capture("ag_grid")
def simple_ag_grid(data_frame, **kwargs):
    print(f"dash_ag_grid -> len: {len(data_frame)}")

    return dag.AgGrid(
        **kwargs,
        columnDefs=[
            {
                'field': col,
                "checkboxSelection": True,
                'filter': True
            } for col in data_frame.columns
        ],
        columnSize="autoSize",  # (Empty-DF) - Does NOT work with
        # columnSize="responsiveSizeToFit", -> (Empty-DF) - WORKS
        # columnSize="sizeToFit", -> (Empty-DF) - Does NOT work
        rowData=data_frame.to_dict('records'),
        defaultColDef={'resizable': True},
        persistence=True,
        persistence_type="local",
        persisted_props=["selectedRows", "filterModel", "rowData"],
        dashGridOptions={
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            # "pagination": True,
            # "paginationPageSize": 3
        }
    )


page_grid = vm.Page(
    title="Graph / AG Grid",
    components=[
        vm.AgGrid(
            id="outer_ag_grid_id",
            figure=simple_ag_grid(data_frame="my_data", id='vizro-grid-id'),
            actions=[
                vm.Action(
                    function=filter_interaction(targets=["outer_ag_grid_id_2"]),
                )
            ]
        ),
        vm.AgGrid(
            id="outer_ag_grid_id_2",
            figure=simple_ag_grid(data_frame="my_data", id='vizro-grid-id-2'),
        ),
    ],
    controls=[
        vm.Filter(
            column="Column 1",
            selector=vm.RangeSlider(min=1, max=10, step=1, value=[1, 10])
        )
    ]
)

page_home = vm.Page(
    title="Page_2",
    components=[vm.Button()],
)

dashboard = vm.Dashboard(pages=[page_home, page_grid])


if __name__ == "__main__":
    # Vizro().build(dashboard).run(debug=False)
    Vizro(suppress_callback_exceptions=True).build(dashboard).run(debug=True)
