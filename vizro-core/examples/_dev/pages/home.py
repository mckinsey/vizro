import dash
from dash import html
import pandas as pd
import dash_ag_grid as dag


df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/wind_dataset.csv")
columnDefs = [
    { 'field': 'direction' },
    { 'field': 'strength' },
    { 'field': 'frequency'},
]

grid = dag.AgGrid(
    id="get-started-example-basic",
    rowData=df.to_dict("records"),
    columnDefs=columnDefs,
)

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content.'),
    grid
])