import dash_ag_grid as dag

from vizro.models.types import capture


@capture("table")
def dash_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid."""
    return dag.AgGrid(
        rowData=data_frame.to_dict("records"), columnDefs=[{"field": col} for col in data_frame.columns], **kwargs
    )
