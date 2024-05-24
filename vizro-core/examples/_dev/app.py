from datetime import date
from typing import Literal
from pydantic import BaseModel, Field
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

from dash_pydantic_form import ModelForm


class Employee(BaseModel):
    first_name: str = Field(title="First name")
    last_name: str = Field(title="Last name")
    office: Literal["au", "uk", "us", "fr"] = Field(title="Office")
    joined: date = Field(title="Employment date")


# somewhere in your layout:
form = ModelForm(
    Employee,
    aio_id="employees",
    form_id="new_employee",
)



df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content'),
    form
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)