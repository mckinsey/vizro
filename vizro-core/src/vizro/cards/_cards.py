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


# Example 1: KPI Card with Markdown
# (+) Allows for unlimited customisation on text
# (-) Custom styling becomes difficult due to className provision
@capture("card")
def kpi_card_mkd(data_frame: pd.DataFrame, title: str, value: str, agg_fct: Callable = sum) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    # LQ: Think about exposing an argument that allows for custom formatting such as formatting as currency
    value = round(agg_fct(data_frame[value]), 2)

    return dcc.Markdown(
        f"""
        ## {title}

        # {value}
        """,
        dangerously_allow_html=False,
    )


# Example 2: KPI Card with HTML
# (-) Customisation on text requires a new captured Callable to be created
# (+) Allows for indefinite custom styling


# LQ: Do we want all of these arguments? `title` and `value` are required, but the rest is extra functionality that
# we could also outsource to creating their own CapturedCallable with that logic. It would be just more cumbersome to create these.
@capture("card")
def kpi_card(
    data_frame: pd.DataFrame,
    title: str,
    value: str,
    icon: Optional[str] = None,
    agg_fct: Callable = sum,
    value_format: Optional[str] = None,
) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = agg_fct(data_frame[value])

    return dbc.Card(
        [
            html.Div(
                [
                    html.P(icon, className="material-symbols-outlined") if icon else None,
                    html.H2(title),
                ],
            ),
            html.P(value_format.format(value) if value_format else value),
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
    agg_fct: Callable = sum,
) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value = agg_fct(data_frame[value])
    ref_value = agg_fct(data_frame[ref_value])
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
