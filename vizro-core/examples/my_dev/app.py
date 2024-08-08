# custom graph/table/grid

"""Example to show dashboard configuration."""
import pandas as pd
import dash_ag_grid as dag


import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.managers import data_manager
from vizro.models.types import capture


@capture("ag_grid")
def custom_ag_grid(data_frame, **kwargs):
    print(f"AG Grid len: {len(data_frame)}")
    vizro_dash_ag_grid = dash_ag_grid(data_frame, **kwargs)
    return vizro_dash_ag_grid()


# data = pd.read_csv("test_data.csv")


data = pd.DataFrame({
    'Column 1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Column 2': ['A', 'B', 'C', 'D', 'Aaksjdaksljdlkasjdlkasjdlkasjlkasjkldaaksjdalksdjlaskkkasldadlksdkaslasdkalsdkasdjalasda', 'F', 'G', 'H', 'I', 'J'],
    'Column 3': [10.5, 20.1, 30.2, 40.3, 50.4, 60.5, 70.6, 80.7, 90.8, 100.9]
})


def load_data():
    return data


data_manager["my_data"] = load_data


@capture("ag_grid")
def simple_ag_grid(data_frame, **kwargs):
    return dag.AgGrid(
        id='grid',
        columnDefs=[{'headerName': col, 'field': col} for col in data_frame.columns],
        columnSize="autoSize",
        rowData=data_frame.to_dict('records'),
        defaultColDef={'resizable': True},
    )


page_grid = vm.Page(
    title="Graph / AG Grid",
    components=[
        # vm.AgGrid(
        #     id="outer_ag_grid_id",
        #     title="AgGrid",
        #     figure=custom_ag_grid(
        #         id="inner_ag_grid_id",
        #         data_frame="my_data",
        #         columnSize="autoSize",  # Does NOT work
        #         # columnSize="responsiveSizeToFit", -> WORKS
        #         # columnSize="sizeToFit", -> Does NOT work
        #         persistence=True,
        #         persistence_type="session",
        #         persisted_props=["filerModel"],
        #         # persisted_props=["columnSize", "filerModel"],
        #         updateColumnState=True,
        #         # columnState
        #         # suppressSizeToFit=True
        #     )
        # ),
        vm.AgGrid(
            figure=simple_ag_grid(data_frame="my_data"),
        )
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



# @callback(
#     Output("column-sizing-size-to-fit-callback", "columnSize"),
#     Input("button-size-to-fit-callback", "n_clicks"),
# )
# def update_column_size_callback(_):
#     return "sizeToFit"


dashboard = vm.Dashboard(pages=[page_home, page_grid])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
