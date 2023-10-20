import pandas as pd
from dash import dash_table

from vizro.models.types import capture


@capture("table")
def dash_data_table(data_frame: pd.DataFrame, **kwargs):
    """Standard `dash_table.DataTable`."""
    kwargs.setdefault("columns", [{"name": i, "id": i} for i in data_frame.columns])
    return dash_table.DataTable(data=data_frame.to_dict("records"), **kwargs)
