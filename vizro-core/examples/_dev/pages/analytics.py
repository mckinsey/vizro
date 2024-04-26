import dash
import dash_ag_grid as dag
import pandas as pd
from dash import Input, Output, callback, dcc, html

# Define some sample data
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
columnDefs = [
    {"field": "this_is_a_really_long_column_name_0"},
    {"field": "short_col_name"},
    {"field": "this_is_a_really_long_column_name_2"},
    {"field": "short"},
    {"field": "this_is_a_really_long_column_name_4"},
    {"field": "this_is_a_really_long_column_name_6"},
    {"field": "short4"},
    {"field": "this_is_a_really_long_column_name_7"},
]

# Create DataFrame
df = pd.DataFrame(data)

grid = dag.AgGrid(
    id="get-started-example-basic",
    rowData=df.to_dict("records"),
    columnDefs=columnDefs,
    columnSize="autoSize",
)

dash.register_page(__name__)

layout = html.Div(
    [
        html.H1("This is our Analytics page"),
        grid,
        html.Div(
            [
                "Select a city: ",
                dcc.RadioItems(
                    options=["New York City", "Montreal", "San Francisco"], value="Montreal", id="analytics-input"
                ),
            ]
        ),
        html.Br(),
        html.Div(id="analytics-output"),
    ]
)


@callback(Output("analytics-output", "children"), Input("analytics-input", "value"))
def update_city_selected(input_value):
    return f"You selected: {input_value}"
