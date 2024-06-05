"""Module containing default card components."""

from typing import Callable, Optional

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, get_relative_path, html

from vizro.models.types import capture


# LQ: The data frame is not used in the function, but needs to be provided here. I guess that is unavoidable for now?
@capture("card")
def text_card(data_frame: pd.DataFrame, text: str) -> dbc.Card:
    """Static text card."""
    return dbc.Card(dcc.Markdown(text, dangerously_allow_html=False))


@capture("card")
def nav_card(data_frame: pd.DataFrame, text: str, href: str) -> dbc.Card:
    """Static navigation card."""
    return dbc.Card(
        dbc.NavLink(
            dcc.Markdown(text, dangerously_allow_html=False),
            href=get_relative_path(href) if href.startswith("/") else href,
        ),
        className="card-nav",
    )


@capture("card")
def kpi_card(
    data_frame: pd.DataFrame,
    column: str,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    agg_func: str = "sum",
    value_format: str = "{value}",
) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = data_frame[column].agg(agg_func)
    title = title or column.title()

    return dbc.Card(
        [
            html.Div(
                [
                    html.P(icon, className="material-symbols-outlined") if icon else None,
                    html.H2(title),
                ],
            ),
            html.P(value_format.format(value=value)),
            # You could specify e.g. value_format = "£{value:0.2f}". Note that
            # arbitrary Python is not allowed here, e.g. you couldn't do something like "{something if value > 0 else
            # something_else}"
            # We might still want some warning about not allowing untrusted user input for your value format string due to
            # https://stackoverflow.com/questions/15356649/can-pythons-string-format-be-made-safe-for-untrusted-format-strings
            # But maybe that's not worth worrying about in practice.
        ],
        className="kpi-card",
    )


# LQ: Not sure if the removal of classNames is a better approach. It seems more unstable as it depends
# on the component hierarchy not changing now. I slightly prefer to explictly provide classNames to the subcomponents here.


# LQ: # In case we do want to go with the `value_format` argument - what's the best way to handle this for e.g. for the kpi_card_ref.
# # Optimally we don't want to have 3 `value_format` arguments for `value`, `ref_value` and `delta`. Provision of fstring?`
@capture("card")
def kpi_card_ref(
    data_frame: pd.DataFrame,
    title: str,
    value: str,
    ref_value: str,
    icon: Optional[str] = None,
    agg_func: Callable = sum,
) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = agg_func(data_frame[value])
    ref_value = agg_func(data_frame[ref_value])
    # LQ: Make it configurable so people can choose percentage or absolute delta?
    delta = round((ref_value - value) / value * 100, 2)
    delta_sign = "delta-pos" if delta > 0 else "delta-neg"

    return dbc.Card(
        [
            html.Div(
                [
                    html.P(icon, className="material-symbols-outlined") if icon else None,
                    html.H2(title),
                ],
            ),
            html.P(value),
            html.Span(
                [
                    html.Span(
                        "arrow_circle_up" if delta > 0 else "arrow_circle_down", className="material-symbols-outlined"
                    ),
                    # LQ: Do we want to make this entire string configurable? e.g. enable provision of fstring?
                    # If yes, check how we evaluate f string only here instead of when being provided.
                    # Provid function?
                    html.Span(f"{delta} % vs. reference ({ref_value})"),
                ],
                className=delta_sign,
            ),
        ],
        className="kpi-card-ref",
    )
