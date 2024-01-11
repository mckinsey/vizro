from vizro.models.types import capture
import dash_ag_grid as dag


@capture("action")
def dash_ag_grid(data_frame=None):
    """Custom AgGrid."""
    return dag.AgGrid(
        id="get-started-example-basic",
        rowData=data_frame.to_dict("records"),
        columnDefs=[{"field": col} for col in data_frame.columns],
    )