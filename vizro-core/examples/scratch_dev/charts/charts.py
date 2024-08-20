"""File to simulate imports from other modules."""

import vizro.models as vm
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro.actions import export_data
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df = px.data.iris()


@capture("ag_grid")
def my_custom_aggrid(chosen_columns, data_frame=None):
    """Custom ag_grid."""
    defaults = {
        "className": "ag-theme-quartz-dark ag-theme-vizro",
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "flex": 1,
            "minWidth": 70,
        },
        "style": {"height": "100%"},
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
    )


page2 = vm.Page(
    title="Page2",
    components=[
        vm.Graph(id="hist_chart2", figure=px.histogram(df, x="sepal_width", color="species")),
        vm.AgGrid(figure=my_custom_aggrid(data_frame="iris", chosen_columns=["sepal_width", "sepal_length"])),
        vm.AgGrid(figure=dash_ag_grid(data_frame="iris")),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=export_data()),
                vm.Action(
                    function=export_data(
                        file_format="xlsx",
                    )
                ),
            ],
        ),
    ],
)
