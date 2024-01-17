import dash_ag_grid as dag

from vizro.models.types import capture


@capture("action")
def dash_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid."""
    return dag.AgGrid(
        id="get-started-example-basic",
        rowData=data_frame.to_dict("records"),
        columnDefs=[{"field": col, "filter": True} for col in data_frame.columns],
        dashGridOptions={"rowHeight": 40},
        **kwargs,
    )
