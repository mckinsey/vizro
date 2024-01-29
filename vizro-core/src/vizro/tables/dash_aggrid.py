import dash_ag_grid as dag

from vizro.models.types import capture
from pandas.api.types import is_numeric_dtype

@capture("action")
def dash_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid."""
    return dag.AgGrid(
        id="get-started-example-basic",
        rowData=data_frame.to_dict("records"),
        columnDefs=[{"field": col, "flex":1, 'type': 'numericColumn' if is_numeric_dtype(data_frame[col].dtype) else None} for col in data_frame.columns],
        **kwargs,
    )
