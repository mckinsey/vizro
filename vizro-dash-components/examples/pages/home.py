"""Home: overview of the vizro-dash-components example app."""

import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(__name__, path="/", order=0)

layout = html.Div(
    [
        dmc.Title("vizro-dash-components examples", order=2, mb="sm"),
        dmc.Text(
            "This app is a small Dash + Mantine playground for Vizro Dash Components (vdc): "
            "custom Dash components you can use on their own or from Vizro dashboards.",
            mb="md",
        ),
    ]
)
