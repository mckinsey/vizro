"""Module containing default card components."""

from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, get_relative_path, html

from vizro.models.types import capture


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



# TBD: names like
# value, value_format, column
# reference, reference_format or comparison_format, reference_column

# TBD merge these two functions into just one? Since the second is just the same as the first with two additional
# arguments. Not sure if good idea or not.
# Can we remove any arguments easily? Don't want them to get too complicated.

# We maybe also need an argument positive_delta_is_good: bool = True(not sure about name) as per #505 (comment).

@capture("card")
def kpi_card_compare(
    data_frame: pd.DataFrame,
    column: str,
    # These two are new:
    reference_column: str,
    comparison_format: str = "{delta_relative:.1%} vs. reference ({reference_value})",  # Note you do percentage
    # calculation using Python formation language itself: https://docs.python.org/3/library/string.html#format-specification-mini-language
    title: Optional[str] = None,
    icon: Optional[str] = None,
    agg_func: str = "sum",
    value_format: str = "{value}",
) -> dbc.Card:
    """Dynamic text card in form of a KPI Card."""
    value, reference_value = data_frame[[column, reference_column]].agg(agg_func)
    title = title or column.title()
    delta = value - reference_value
    delta_relative = delta / reference_value

    # Variables available in both comparison_format and value_format are value, reference_value, delta, delta_relative
    return dbc.Card(
        [
        html.Div(
            [
                html.P(icon, className="material-symbols-outlined") if icon else None,
                html.H2(title),
            ],
        ),
        html.P(value_format.format(value=value, reference_value=reference_value, delta=delta,
                                   delta_relative=delta_relative)),
        html.Span(
            [
                html.Span(
                    "arrow_circle_up" if delta > 0 else "arrow_circle_down", className="material-symbols-outlined"
                ),
                html.Span(comparison_format.format(value=value, reference_value=reference_value, delta=delta,
                                                   delta_relative=delta_relative)),
            ],
            className="delta-pos" if delta > 0 else "delta-neg",
        ),
    ], className="kpi-card-compare")
