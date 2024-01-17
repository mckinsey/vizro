"""Module containing the standard implementation of `dash-ag-grid.AgGrid`."""
import dash_ag_grid as dag
import pandas as pd

from vizro.models.types import capture
from vizro.tables.tables_utils import _set_defaults_nested


@capture("action")
def dash_ag_grid(data_frame: pd.DataFrame = None, **kwargs):
    """Standard `dash-ag-grid.AgGrid`."""
    defaults = {
        "columnDefs": [{"field": col, "filter": True} for col in data_frame.columns],
        "className": "ag-theme-alpine vizro",
        "rowData": data_frame.to_dict("records"),
        "dashGridOptions": {"rowHeight": 40},
        "defaultColDef": {"resizable": True, "sortable": True},
        "columnSize": "sizeToFit",
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dag.AgGrid(**kwargs)
