"""Example to show dashboard configuration specified as pydantic models."""
import os

# import d3_bar_chart
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture
import vizro.plotly.express as px
from vizro.actions import filter_interaction, export_data


def retrieve_table_data():
    """Return data for table for testing."""
    states = [
            "California",
            "Arizona",
            "Nevada",
            "New Mexico",
            "Colorado",
            "Texas",
            "North Carolina",
            "New York",
        ]

    data = {
        "State": states + states[::-1],
        "Number of Solar Plants": [289, 48, 11, 33, 20, 12, 148, 13] * 2,
        "Installed Capacity (MW)": [4395, 1078, 238, 261, 118, 187, 669, 53] * 2,
        "Average MW Per Plant": [15.3, 22.5, 21.6, 7.9, 5.9, 15.6, 4.5, 4.1] * 2,
        "Generation (GWh)": [10826, 2550, 557, 590, 235, 354, 1162, 84] * 2,
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


# @capture("graph")
# def d3_bar(data_frame=None):
#    """Custom table."""
#    return d3_bar_chart.D3BarChart(
#        id="input",
#        value="my-value",
#        label="my-label",
#    )


@capture("graph")
def table_dash(data_frame=None, style_header=None, **kwargs):
    """Custom table."""
    return dash_table.DataTable(

        # PP: Don't know a better way how to insert the 'id' into datatable than manually.
        id="datatable_id",

        data=data_frame.to_dict("records"),
        columns=[{"name": i, "id": i} for i in data_frame.columns],
        style_header=style_header,
        # page_size=6,
        **kwargs
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
        vm.Table(
            id="datatable_id",
            figure=table_dash(
                data_frame="table_data"
            ),
            actions=[vm.Action(function=filter_interaction(targets=["scatter_chart"]))]
        ),
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(
                data_frame="table_data",
                x="State",
                y="Number of Solar Plants",
                color="Number of Solar Plants",
                custom_data=["State"]
            ),
            actions=[vm.Action(function=filter_interaction(targets=["datatable_id"]))]
        ),
        # vm.React(id="d3_bar", figure=d3_bar(data_frame="table_data")),
        vm.Button(
            id='export_data_button',
            actions=[vm.Action(function=export_data())]
        )
    ],
    controls=[
        vm.Filter(column="State", selector=vm.Dropdown()),
        vm.Parameter(targets=["graph.x"], selector=vm.RadioItems(options=["petal_length", "sepal_length"])),
    ],
)
dashboard = vm.Dashboard(pages=[page_0])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()
