"""Module containing default card components."""

from typing import Callable

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, get_relative_path, html

from vizro.models.types import capture

# TODO: Check if we can get rid of any of these issues:
# 1) The data frame is not used in the function, but needs to be provided here


@capture("card")
def text_card(data_frame: pd.DataFrame, text: str) -> dbc.Card:
    """Static text card."""
    return dcc.Markdown(text, dangerously_allow_html=False)


@capture("card")
def nav_card(data_frame: pd.DataFrame, text: str, href: str) -> dbc.Card:
    """Static navigation card."""
    return dbc.NavLink(
        dcc.Markdown(text, dangerously_allow_html=False),
        href=get_relative_path(href) if href.startswith("/") else href,
    )


# LQ: All of the below don't have to be official Vizro KPI Cards, but can be examples of how to create custom cards
# These can also just live in the docs as examples if not suitable for common usage.


# Example 1: Aggregated KPI Card with Markdown
# (+) Allows for unlimited customisation on text
# (-) Custom styling becomes difficult
@capture("card")
def kpi_card_agg(data_frame: pd.DataFrame, title: str, value: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = round(agg_fct(data_frame[value]), 2)

    return dcc.Markdown(
        f"""
        ## {title}

        # {value}
        """,
        dangerously_allow_html=False,
    )


@capture("card")
def kpi_card_ref(data_frame: pd.DataFrame, title: str, value: str, ref_value: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = round(agg_fct(data_frame[value]), 2)
    ref_value = round(agg_fct(data_frame[ref_value]), 2)
    delta = round((ref_value - value) / value * 100, 2)
    color = "up" if delta > 0 else "down"

    return [
        html.H2(title, className="kpi-title"),
        html.P(value, className="kpi-value"),
        html.Span(
            [
                html.Span(
                    "arrow_circle_up" if delta > 0 else "arrow_circle_down", className="material-symbols-outlined"
                ),
                html.Span(f"{delta} % vs. Reference ({ref_value})"),
            ],
            className=f"kpi-ref-value {color}",
        ),
    ]


@capture("card")
def kpi_card_icon(data_frame: pd.DataFrame, title: str, value: str, icon: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = round(agg_fct(data_frame[value]), 2)

    return [
        html.Div(
            [
                html.P(icon, className="kpi-icon material-symbols-outlined"),
                html.H2(title),
            ],
            className="kpi-title",
        ),
        html.P(value, className="kpi-value"),
    ]
