"""Example to show dashboard configuration specified as pydantic models."""
import os

import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc

import vizro.models as vm
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

def retrieve_table_data():
    """Return data for table for testing."""
    data = {
        "State": [
            "California",
            "Arizona",
            "Nevada",
            "New Mexico",
            "Colorado",
            "Texas",
            "North Carolina",
            "New York",
        ],
        "Number of Solar Plants": [289, 48, 11, 33, 20, 12, 148, 13],
        "Installed Capacity (MW)": [4395, 1078, 238, 261, 118, 187, 669, 53],
        "Average MW Per Plant": [15.3, 22.5, 21.6, 7.9, 5.9, 15.6, 4.5, 4.1],
        "Generation (GWh)": [10826, 2550, 557, 590, 235, 354, 1162, 84],
    }

    return pd.DataFrame(data)



# Option 1: Use graph objects table
@capture("graph")
def table_go(data_frame=None, template=None):
    """Custom table."""
    return go.Figure(
        data=[
            go.Table(
                header={"values": data_frame.columns.to_list()},
                cells={"values": data_frame.values.transpose().tolist()},
            )
        ]
    )



@capture("action")
def table_dash(data_frame=None, style_header=None):
    """Custom table."""
    return dash_table.DataTable(
                data=data_frame.to_dict("records"),
                columns=[{"name": i, "id": i} for i in data_frame.columns],
                style_header=style_header)


@capture("action")
def markdown(data_frame=None):
    """Custom table."""
    return dcc.Markdown(f"Data columns: {data_frame.columns.to_list()}")


data_manager["table_data"] = retrieve_table_data
data = retrieve_table_data()

page_0 = vm.Page(
    title="Color manager",
    path="color-manager",
    components=[
        # Option 1
        # vm.Graph(
        #     id="go_table",
        #     figure=table_go(data_frame='table_data'),
        # ),
        # Option 2
        # vm.Table(data_frame="table_data", style_header={ 'border': '1px solid black' }),
        # Option 3 with pd.DataFrame()
      #  vm.Table(
      #      id="table1",
      #      figure=table_dash(
      #          data_frame=pd.DataFrame({"A": 1.0, "B": pd.Series(1, index=list(range(4)), dtype="float32")})
      #      ),
       # ),
        # Option 3 with str
        vm.React(id="table2", figure=table_dash(data_frame="table_data")),
        # Option 3 with different react model
        # vm.React(id="table3",
        #          figure=markdown(data_frame='table_data')
        #          )
    ],
    controls=[
        vm.Filter(column="State", selector=vm.Dropdown()),
        # vm.Parameter(targets=["table2.figure.page_size"], selector=vm.RadioItems(options=[3,5]))
    ],
)
dashboard = vm.Dashboard(pages=[page_0])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()