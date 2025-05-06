"""Contains default KPI card functions."""

from typing import Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import html

from vizro.models.types import capture


@capture("figure")
def kpi_card(
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: Optional[str] = None,
    icon: Optional[str] = None,
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value.

    **Warning:** Note that the format string provided to `value_format` is being evaluated, so ensure that only trusted
    user input is provided to prevent potential security risks.

    Args:
        data_frame: DataFrame containing the data.
        value_column: Column name of the value to be shown.
        value_format: Format string to be applied to the value. It must be a
            [valid Python format](https://docs.python.org/3/library/string.html#format-specification-mini-language)
            string where any of the below placeholders can be used. Defaults to "{value}".

            - value: `value_column` aggregated by `agg_func`.

            **Common examples include:**

             - "{value}": Displays the raw value.
             - "${value:0.2f}": Formats the value as a currency with two decimal places.
             - "{value:.0%}": Formats the value as a percentage without decimal places.
             - "{value:,}": Formats the value with comma as a thousands separator.

        agg_func: String function name to be used for aggregating the data. Common options include
            "sum", "mean" or "median". Default is "sum". For more information on possible functions, see
            https://stackoverflow.com/questions/65877567/passing-function-names-as-strings-to-pandas-groupby-aggregrate.
        title: KPI title displayed on top of the card. If not provided, it defaults to the capitalized `value_column`.
        icon: Name of the icon from the [Google Material Icon Library](https://fonts.google.com/icons) to be displayed
            on the left side of the KPI title. If not provided, no icon is displayed.

    Returns:
         A Dash Bootstrap Components card (`dbc.Card`) containing the formatted KPI value.

    Examples:
        Wrap inside `vm.Figure` to use as a component inside `vm.Page` or `vm.Container`.
        >>> import vizro.models as vm
        >>> from vizro.figures import kpi_card
        >>> vm.Page(title="Page", components=[vm.Figure(figure=kpi_card(...))])

    """
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    header = dbc.CardHeader(
        [
            html.P(icon, className="material-symbols-outlined") if icon else None,
            html.H4(title, className="card-kpi-title"),
        ]
    )
    body = dbc.CardBody(value_format.format(value=value))
    return dbc.Card([header, body], class_name="card-kpi")


@capture("figure")
def kpi_card_reference(  # noqa: PLR0913
    data_frame: pd.DataFrame,
    value_column: str,
    reference_column: str,
    *,
    value_format: str = "{value}",
    reference_format: str = "{delta_relative:+.1%} vs. reference ({reference})",
    agg_func: str = "sum",
    title: Optional[str] = None,
    icon: Optional[str] = None,
    reverse_color: bool = False,
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value in comparison to a reference value.

    **Warning:** Note that the format string provided to `value_format` and `reference_format` is being evaluated,
    so ensure that only trusted user input is provided to prevent potential security risks.

    Args:
        data_frame: DataFrame containing the data.
        value_column: Column name of the value to be shown.
        reference_column: Column name of the reference value for comparison.
        value_format: Format string to be applied to the value. It must be a
            [valid Python format](https://docs.python.org/3/library/string.html#format-specification-mini-language)
            string where any of the below placeholders can be used. Defaults to "{value}".

            - value: `value_column` aggregated by `agg_func`.
            - reference: `reference_column` aggregated by `agg_func`.
            - delta: Difference between `value` and `reference`.
            - delta_relative: Relative difference between `value` and `reference`.

            **Common examples include:**

             - "{value}": Displays the raw value.
             - "${value:0.2f}": Formats the value as a currency with two decimal places.
             - "{value:.0%}": Formats the value as a percentage without decimal places.
             - "{value:,}": Formats the value with comma as a thousands separator.

        reference_format: Format string to be applied to the reference. For more details on possible placeholders, see
            docstring on `value_format`. Defaults to "{delta_relative:+.1%} vs. reference ({reference})".
        agg_func: String function name to be used for aggregating the data. Common options include
            "sum", "mean" or "median". Default is "sum". For more information on possible functions, see
            https://stackoverflow.com/questions/65877567/passing-function-names-as-strings-to-pandas-groupby-aggregrate.
        title: KPI title displayed on top of the card. If not provided, it defaults to the capitalized `value_column`.
        icon: Name of the icon from the [Google Material Icon Library](https://fonts.google.com/icons) to be displayed
            on the left side of the KPI title. If not provided, no icon is displayed.
        reverse_color: If `False`, a positive delta will be colored positively (e.g., blue) and a negative delta
            negatively (e.g., red). If `True`, the colors will be inverted: a positive delta will be colored
            negatively (e.g., red) and a negative delta positively (e.g., blue). Defaults to `False`.



    Returns:
        A Dash Bootstrap Components card (`dbc.Card`) containing the formatted KPI value and reference.

    Examples:
        Wrap inside `vm.Figure` to use as a component inside `vm.Page` or `vm.Container`.
        >>> import vizro.models as vm
        >>> from vizro.figures import kpi_card_reference
        >>> vm.Page(title="Page", components=[vm.Figure(figure=kpi_card_reference(...))])

    """
    title = title or f"{agg_func} {value_column}".title()
    value, reference = data_frame[[value_column, reference_column]].agg(agg_func)
    delta = value - reference
    delta_relative = delta / reference if reference else np.nan
    pos_color, neg_color = ("color-neg", "color-pos") if reverse_color else ("color-pos", "color-neg")
    footer_class = pos_color if delta > 0 else neg_color if delta < 0 else ""

    header = dbc.CardHeader(
        [
            html.P(icon, className="material-symbols-outlined") if icon else None,
            html.H4(title, className="card-kpi-title"),
        ]
    )
    body = dbc.CardBody(
        value_format.format(value=value, reference=reference, delta=delta, delta_relative=delta_relative)
    )
    footer = dbc.CardFooter(
        [
            html.Span(
                "arrow_circle_up" if delta > 0 else "arrow_circle_down" if delta < 0 else "arrow_circle_right",
                className="material-symbols-outlined",
            ),
            html.Span(
                reference_format.format(value=value, reference=reference, delta=delta, delta_relative=delta_relative)
            ),
        ],
        class_name=footer_class,
    )
    return dbc.Card([header, body, footer], class_name="card-kpi")
