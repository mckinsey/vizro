"""Module containing default card components."""

from typing import Callable

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, get_relative_path, html

from vizro.models.types import capture

# TODO: Check if we can get rid of any of these issues:
# 1) The data frame is not used in the function, but needs to be provided here
# 2) id needs to be passed on through the CapturedCallable so the responsive sub-component of the Card receives it


@capture("card")
def text_card(data_frame: pd.DataFrame, text: str, id: str) -> dbc.Card:
    """Static text card."""
    return dbc.Card(dcc.Markdown(text, dangerously_allow_html=False, id=id))


@capture("card")
def nav_card(data_frame: pd.DataFrame, text: str, href: str, id: str) -> dbc.Card:
    """Static navigation card."""
    return dbc.Card(
        dbc.NavLink(
            dcc.Markdown(text, dangerously_allow_html=False, id=id),
            href=get_relative_path(href) if href.startswith("/") else href,
        ),
        className="card-nav",
    )


# TODO: Add 1-2 other KPI card stylings
# LQ: All of the below don't have to be official Vizro KPI Cards, but can be examples of how to create custom cards
# These can also just live in the docs as examples if not suitable for common usage.


# Example 1: Aggregated KPI Card with Markdown
@capture("card")
def kpi_card_agg(data_frame: pd.DataFrame, title: str, id: str, value: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = agg_fct(data_frame[value])

    return dbc.Card(
        dcc.Markdown(
            f"""
        ### {title}

        ## {value}
        """,
            dangerously_allow_html=False,
            id=id,
        ),
    )


@capture("card")
def kpi_card_ref(data_frame: pd.DataFrame, title: str, id: str, value: str, ref_value: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = agg_fct(data_frame[value])
    ref_value = agg_fct(data_frame[ref_value])
    delta = (ref_value-value)/value * 100
    icon = "arrow_circle_up" if delta > 0 else "arrow_circle_down"

    return dbc.Card(
            [
                html.H4(title, className="card-title"),
                html.P(value, className="card-value"),
                html.Span(
                    [
                        html.Span(icon, className=f"material-symbols-outlined {icon}"),
                        html.Span(ref_value, className=icon),
                    ],
                    className="card-ref-value",
                ),
            ],
            className=f"card-{icon}",
        )
