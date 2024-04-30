from collections import defaultdict
from typing import Any, Dict, Mapping

import dash
import dash_ag_grid as dag
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc


# AG Grid as in core code
def _set_defaults_nested(supplied: Mapping[str, Any], defaults: Mapping[str, Any]) -> Dict[str, Any]:
    supplied = defaultdict(dict, supplied)
    for default_key, default_value in defaults.items():
        if isinstance(default_value, Mapping):
            supplied[default_key] = _set_defaults_nested(supplied[default_key], default_value)
        else:
            supplied.setdefault(default_key, default_value)
    return dict(supplied)


def dash_ag_grid(data_frame: pd.DataFrame, **kwargs) -> dag.AgGrid:
    """Implementation of `dash_ag_grid.AgGrid` with sensible defaults to be used in [`AgGrid`][vizro.models.AgGrid]."""
    defaults = {
        # "className": "ag-theme-quartz-dark ag-theme-vizro",
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
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "flex": 1,
            "minWidth": 70,
        },
        "dashGridOptions": {
            "animateRows": False,
            "pagination": True,
        },
        # "style": {"height": "100%"},
    }
    kwargs = _set_defaults_nested(kwargs, defaults)
    return dag.AgGrid(**kwargs)


# DATA
data = {
    "this_is_a_really_long_column_name_0": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short_col_name": [4, 5, 6],
    "this_is_a_really_long_column_name_2": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short": [10, 11, 12],
    "this_is_a_really_long_column_name_4": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "this_is_a_really_long_column_name_6": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short4": [10, 11, 12],
    "this_is_a_really_long_column_name_7": [13, 14, 15],
}

df = pd.DataFrame(data)

# Testing out:
# columnSize
# Persistence
grid = html.Div(dash_ag_grid(
    data_frame=df, id="persistence-grid", columnSize="autoSize", persistence=True, persisted_props=["filterModel"]
), id="persistence-grid-div")

dash.register_page(__name__, path="/")


# @dash.callback(
#     dash.Output("persistence-grid-div", "children"),
#             dash.Input("example-button", "n_clicks"))
# def update_grid(n_clicks):
#     if n_clicks is None:
#         dash.exceptions.PreventUpdate
#     return dash_ag_grid(
#     data_frame=df, id="persistence-grid"#, columnSize="autoSize", persistence=True, persisted_props=["filterModel"]
# )


layout = html.Div([html.H1("This is our Home page"), grid,
                   # dbc.Button(
                   #     "Click me", id="example-button", className="me-2", n_clicks=0
                   # )
                   ])
