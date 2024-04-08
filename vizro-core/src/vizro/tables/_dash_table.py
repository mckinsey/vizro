"""Module containing the standard implementation of `dash_table.DataTable`."""

import pandas as pd
from dash import dash_table

from vizro.models.types import capture
from vizro.tables._utils import _set_defaults_nested


@capture("table")
def dash_data_table(data_frame: pd.DataFrame, **kwargs) -> dash_table.DataTable:
    """Standard `dash_table.DataTable` with sensible defaults to be used in [`Table`][vizro.models.Table]."""
    defaults = {
        "columns": [{"name": col, "id": col} for col in data_frame.columns],
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--state-overlays-selected-hover)",
            "border_top": "1px solid var(--main-container-bg-color)",
            "height": "32px",
        },
        "style_data_conditional": [
            {
                "if": {"state": "active"},
                "backgroundColor": "var(--state-overlays-selected)",
                "border": "1px solid var(--state-overlays-selected)",
            }
        ],
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dash_table.DataTable(data=data_frame.to_dict("records"), **kwargs)
