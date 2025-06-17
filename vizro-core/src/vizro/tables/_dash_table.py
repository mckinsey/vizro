"""Module containing the standard implementation of `dash_table.DataTable`."""

from typing import Any

import pandas as pd
from dash import dash_table

from vizro._vizro_utils import _set_defaults_nested
from vizro.models.types import capture


@capture("table")
def dash_data_table(data_frame: pd.DataFrame, **kwargs: Any) -> dash_table.DataTable:
    """Standard `dash.dash_table.DataTable` with sensible defaults to be used in [`Table`][vizro.models.Table].

    Args:
        data_frame: DataFrame containing the data to be displayed.
        kwargs: Additional keyword arguments to be passed to the `dash_table.DataTable` component.

    Returns:
        A `dash.dash_table.DataTable` component with sensible defaults.

    Examples:
        Wrap inside `vm.Table` to use as a component inside `vm.Page` or `vm.Container`.
        >>> import vizro.models as vm
        >>> from vizro.table import dash_data_table
        >>> vm.Page(title="Page", components=[vm.Table(figure=dash_data_table(...))])

    """
    defaults = {
        "columns": [{"name": col, "id": col} for col in data_frame.columns],
        "style_as_list_view": True,
        "style_cell": {"position": "static"},
        "style_data": {"border_bottom": "1px solid var(--border-subtleAlpha01)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--stateOverlays-selectedHover)",
            "border_top": "None",
            "height": "32px",
        },
        "style_data_conditional": [
            {
                "if": {"state": "active"},
                "backgroundColor": "var(--stateOverlays-selected)",
                "border": "1px solid var(--stateOverlays-selected)",
            }
        ],
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dash_table.DataTable(data=data_frame.to_dict("records"), **kwargs)
