"""Example to show dashboard configuration specified as pydantic models."""
import os

# import d3_bar_chart
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc

import vizro.models as vm
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture
import vizro.plotly.express as px


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


#@capture("graph")
#def d3_bar(data_frame=None):
#    """Custom table."""
#    return d3_bar_chart.D3BarChart(
#        id="input",
#        value="my-value",
#        label="my-label",
#    )


@capture("action")
def table_dash(data_frame=None, style_header=None):
    """Custom table."""
    return dash_table.DataTable(
        data=data_frame.to_dict("records"),
        columns=[{"name": i, "id": i} for i in data_frame.columns],
        style_header=style_header,
    )


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
        vm.Table(id="table2", figure=table_dash(data_frame="table_data",style_header={ 'border': '1px solid green' })),
        vm.Graph(id="graph", figure=px.scatter(data_frame=px.data.iris(),x="sepal_width",y="sepal_length",color="species")),
    ],
    controls=[
        vm.Filter(column="State", selector=vm.Dropdown()),
        vm.Parameter(targets=["table2.style_header.border"], selector=vm.RadioItems(options=["1px solid green","1px solid pink"])),
        vm.Parameter(targets=["graph.x"], selector=vm.RadioItems(options=["petal_length","sepal_length"]))
    ],
)
dashboard = vm.Dashboard(pages=[page_0])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()