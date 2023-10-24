"""Example to show dashboard configuration specified as pydantic models."""
import os

import dash_ag_grid as dag

# import d3_bar_chart
import pandas as pd
from dash import dash_table

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_data_table
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_data_table


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


@capture("table")
def AgGrid(data_frame=None):
    """Custom AgGrid."""
    return dag.AgGrid(
        id="get-started-example-basic",
        rowData=data_frame.to_dict("records"),
        columnDefs=[{"field": col} for col in data_frame.columns],
        # className="ag-theme-alpine-dark",
    )


data_manager["table_data"] = retrieve_table_data
data = retrieve_table_data()

# TODO: Check the Page.layout. There seem to be some issues when there are several tables on a page.
page_0 = vm.Page(
    title="Color manager",
    path="color-manager",
    components=[
        vm.Table(
            id="table_id",
            figure=dash_data_table(
                id="dash_datatable_id",
                data_frame="table_data",
                style_header={"border": "1px solid green"},
            ),
            actions=[vm.Action(id="filter_interaction", function=filter_interaction(targets=["scatter_chart"]))],
        ),
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(
                data_frame="table_data",
                x="State",
                y="Number of Solar Plants",
                color="Number of Solar Plants",
                custom_data=["State"],
            ),
            actions=[vm.Action(function=filter_interaction(targets=["table_id"]))],
        ),
        vm.Table(
            id="table_2_id",
            figure=dash_data_table(id="dash_datatable_id_2", data_frame=data, style_header={"border": "1px solid green"}),
            actions=[vm.Action(id="filter_interaction_2", function=filter_interaction(targets=["scatter_chart"]))]
        ),
        # vm.Table(
        #     id="ag_grid",
        #     table=AgGrid(data_frame="table_data"),
        #     # TODO: Probably we need to enable filter_interactions out of the box only for AgGrid objects.
        #     # actions=[vm.Action(id="filter_interaction_2", function=filter_interaction(targets=["scatter_chart"]))]
        # ),
        vm.Button(id="export_data_button", actions=[vm.Action(function=export_data())]),
    ],
    controls=[
        vm.Filter(column="State", selector=vm.Dropdown()),
        vm.Parameter(
            targets=["table_id.style_header.border", "table_2_id.style_header.border"],
            selector=vm.RadioItems(options=["1px solid green", "1px solid pink"]),
        ),
    ],
)
dashboard = vm.Dashboard(pages=[page_0])

if __name__ == "__main__":
    # data_manager["table_data"] = retrieve_table_data
    # data = retrieve_table_data()
    # print(vm.Table(id="table2", table=dash_data_table(data, style_header={"border": "1px solid green"}))())
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro().build(dashboard).run()
