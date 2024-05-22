"""Module containing the standard implementation of `dash_table.DataTable`."""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, dcc, get_relative_path, html

from vizro.models.types import capture

# TODO: Check if we can get rid of any of these issues:
# 1) The data frame is not used in the function, but needs to be provided here
# 2) id is usually attached to Card.text, but we append it to the Card itself


@capture("card")
def text_card(data_frame: pd.DataFrame, text: str) -> dash_table.DataTable:
    """Static text card."""
    return dbc.Card(dcc.Markdown(text, dangerously_allow_html=False))  # id should be given to text component


@capture("card")
def nav_card(data_frame: pd.DataFrame, text: str, href: str) -> dash_table.DataTable:
    """Static text card."""
    return dbc.Card(
        dbc.NavLink(
            dcc.Markdown(text, dangerously_allow_html=False),
            href=get_relative_path(href) if href.startswith("/") else href,
        ),
        className="card-nav",
    )


@capture("card")
def kpi_card(data_frame: pd.DataFrame, title: str, value: str) -> dash_table.DataTable:
    """Static text card."""
    value = data_frame[value].sum()

    return dbc.Card(
        [
            html.H4(title, className="card-title"),
            html.P(value, className="card-value"),
        ],
    )
