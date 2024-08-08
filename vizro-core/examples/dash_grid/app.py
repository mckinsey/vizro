import dash
from dash import dcc, html, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd


# Initialize the Dash app
app = dash.Dash(__name__)


# Sample data
df = pd.DataFrame({
    'Column 1': [1, 2, 3, 4, 5, 6],
    'Column 2': ['A', 'B', 'C', 'VeryLongStringInputCell_VeryLongStringInputCell_VeryLongStringInputCell', 'D', 'E'],
    'Column 3': [10.5, 20.1, 30.2, 40.3, 50.4, 60.5],
})

# Layout
app.layout = html.Div([
    html.H1('Grid Page'),
    html.Div(id="outer_div_grid_id"),
    dcc.RangeSlider(id="filter_column_1_dropdown", min=1, max=6, step=1, value=[1, 6]),
])


@callback(
    Output("outer_div_grid_id", "children"),
    Input("filter_column_1_dropdown", "value"),
)
def update_outer_grid(dropdown_value):
    df_filtered = df[df["Column 1"].between(dropdown_value[0], dropdown_value[1], inclusive="both")]

    return [dag.AgGrid(
        id='grid_id',
        columnDefs=[{'field': col} for col in df.columns],
        columnSize="autoSize",
        rowData=df_filtered.to_dict('records'),
        defaultColDef={'resizable': True},
    )]


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
