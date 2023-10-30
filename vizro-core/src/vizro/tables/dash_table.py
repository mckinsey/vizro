"""Module containing the standard implementation of `dash_table.DataTable`."""
from collections import defaultdict
from typing import Any, Dict, Mapping

import pandas as pd
from dash import dash_table

from vizro.models.types import capture


def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> Dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)


@capture("table")
def dash_data_table(data_frame: pd.DataFrame, **kwargs):
    """Standard `dash_table.DataTable`."""
    defaults = {
        "columns": [{"name": i, "id": i} for i in data_frame.columns],
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--state-overlays-selected-hover)",
            "border_top": "1px solid var(--main-container-bg-color)",
            "height": "32px",
        },
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dash_table.DataTable(data=data_frame.to_dict("records"), **kwargs)
