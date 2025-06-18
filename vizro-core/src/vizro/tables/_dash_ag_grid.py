"""Module containing the standard implementation of `dash_ag_grid.AgGrid`."""

from typing import Any

import dash_ag_grid as dag
import pandas as pd

from vizro._vizro_utils import _set_defaults_nested
from vizro.models.types import capture

_FORMAT_CURRENCY_EU = """d3.formatLocale({
  "decimal": ",",
  "thousands": "\u00a0",
  "grouping": [3],
  "currency": ["", "\u00a0€"],
  "percent": "\u202f%",
  "nan": ""
})"""

_DATA_TYPE_DEFINITIONS = {
    "number": {
        "baseDataType": "number",
        "extendsDataType": "number",
        "columnTypes": "rightAligned",
        "appendColumnTypes": True,
        "valueFormatter": {"function": "params.value == null ? 'NaN' : String(params.value)"},
    },
    "dollar": {
        "baseDataType": "number",
        "extendsDataType": "number",
        "valueFormatter": {"function": "d3.format('($,.2f')(params.value)"},
    },
    "euro": {
        "baseDataType": "number",
        "extendsDataType": "number",
        "valueFormatter": {"function": f"{_FORMAT_CURRENCY_EU}.format('$,.2f')(params.value)"},
    },
    "percent": {
        "baseDataType": "number",
        "extendsDataType": "number",
        "valueFormatter": {"function": "d3.format(',.1%')(params.value)"},
    },
    "numeric": {
        "baseDataType": "number",
        "extendsDataType": "number",
        "valueFormatter": {"function": "d3.format(',.1f')(params.value)"},
    },
}


@capture("ag_grid")
def dash_ag_grid(data_frame: pd.DataFrame, **kwargs: Any) -> dag.AgGrid:
    """Implementation of `dash_ag_grid.AgGrid` with sensible defaults to be used in [`AgGrid`][vizro.models.AgGrid].

    Args:
        data_frame: DataFrame containing the data to be displayed.
        kwargs: Additional keyword arguments to be passed to the `dash_ag_grid.AgGrid` component.

    Returns:
        A `dash_ag_grid.AgGrid` component with sensible defaults.

    Examples:
        Wrap inside `vm.AgGrid` to use as a component inside `vm.Page` or `vm.Container`.
        >>> import vizro.models as vm
        >>> from vizro.tables import dash_ag_grid
        >>> vm.Page(title="Page", components=[vm.AgGrid(figure=dash_ag_grid(...))])

    """
    defaults = {
        "className": "ag-theme-quartz-dark ag-theme-vizro",
        "columnDefs": [{"field": col} for col in data_frame.columns],
        "rowData": data_frame.apply(
            lambda x: (
                x.dt.strftime("%Y-%m-%d")  # set date columns to `dateString` for AG Grid filtering to function
                if pd.api.types.is_datetime64_any_dtype(x)
                else x
            )
        ).to_dict("records"),
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
        },
        "dashGridOptions": {
            "dataTypeDefinitions": _DATA_TYPE_DEFINITIONS,
            "animateRows": False,
        },
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dag.AgGrid(**kwargs)
