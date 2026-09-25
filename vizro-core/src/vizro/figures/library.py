"""Contains unwrapped KPI card functions (suitable to use in pure Dash app)."""

import math
from typing import Literal

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

from vizro.models._models_utils import validate_icon

__all__ = ["kpi_card", "kpi_card_reference", "kpi_sparkline_card"]

_SIZE_CLASSES = {"compact": "card-kpi-compact", "default": "", "large": "card-kpi-large"}


def _kpi_card_class_name(size: Literal["compact", "default", "large"]) -> str:
    if size not in _SIZE_CLASSES:
        raise ValueError(f"Invalid size {size!r}. size must be one of {list(_SIZE_CLASSES)}.")
    return f"card-kpi {_SIZE_CLASSES[size]}".strip()


def kpi_card(  # noqa: PLR0913
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: str | None = None,
    icon: str | None = None,
    units: str | None = None,
    size: Literal["compact", "default", "large"] = "default",
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value.

    !!! warning
        The format string provided to `value_format` is evaluated, so ensure that only trusted
        user input is provided to prevent potential security risks.

    Args:
        data_frame: DataFrame containing the data.
        value_column: Column name of the value to be shown.
        value_format: Format string to be applied to the value. It must be a
            [valid Python format](https://docs.python.org/3/library/string.html#format-specification-mini-language)
            string where any of the below placeholders can be used.

            - value: `value_column` aggregated by `agg_func`.

            **Common examples include:**

             - `"{value}"`: Displays the raw value.
             - `"${value:0.2f}"`: Formats the value as a currency with two decimal places.
             - `"{value:.0%}"`: Formats the value as a percentage without decimal places.
             - `"{value:,}"`: Formats the value with comma as a thousands separator.

        agg_func: String function name to be used for aggregating the data. Common options include
            `"sum"`, `"mean"` or `"median"`. [More information on possible
            functions](https://stackoverflow.com/q/65877567).
        title: KPI title displayed on top of the card. If not provided, it defaults to the capitalized
            `value_column`.
        icon: Name of the icon from the [Google Material Icon Library](https://fonts.google.com/icons)
            to be displayed on the left side of the KPI title. If not provided, no icon is displayed.
        units: Unit label (for example `"%"` or `"kg"`) displayed directly after the value in a smaller,
            muted style. If not provided, no unit is displayed.
        size: Size of the card. Possible values are `"compact"`, `"default"` or `"large"`. Defaults to `"default"`.

    Returns:
         A Dash Bootstrap Components card (`dbc.Card`) containing the formatted KPI value.

    Example:
        ```python
        import vizro.models as vm
        from vizro.figures import kpi_card

        vm.Figure(figure=kpi_card(...))
        ```
    """
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    header = dbc.CardHeader(
        [
            html.H4(title, className="card-kpi-title"),
            html.P(validate_icon(icon), className="material-symbols-outlined") if icon else None,
        ],
        className="card-kpi-header",
    )
    body = dbc.CardBody(
        [value_format.format(value=value), html.Span(units, className="card-kpi-units") if units else None]
    )
    return dbc.Card([header, body], class_name=_kpi_card_class_name(size))


def kpi_card_reference(  # noqa: PLR0913
    data_frame: pd.DataFrame,
    value_column: str,
    reference_column: str,
    *,
    value_format: str = "{value}",
    delta_format: str = "{delta_relative:+.1%}",
    reference_format: str = "vs. reference ({reference})",
    agg_func: str = "sum",
    title: str | None = None,
    icon: str | None = None,
    units: str | None = None,
    reverse_color: bool = False,
    size: Literal["compact", "default", "large"] = "default",
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value in comparison to a reference value.

    !!! warning
        The format string provided to `value_format`, `delta_format` and `reference_format` is evaluated, so ensure
        that only trusted user input is provided to prevent potential security risks.

    Args:
        data_frame: DataFrame containing the data.
        value_column: Column name of the value to be shown.
        reference_column: Column name of the reference value for comparison.
        value_format: Format string to be applied to the value. It must be a
            [valid Python format](https://docs.python.org/3/library/string.html#format-specification-mini-language)
            string where any of the below placeholders can be used.

            - value: `value_column` aggregated by `agg_func`.
            - reference: `reference_column` aggregated by `agg_func`.
            - delta: Difference between `value` and `reference`.
            - delta_relative: Relative difference between `value` and `reference`.

            **Common examples include:**

             - `"{value}"`: Displays the raw value.
             - `"${value:0.2f}"`: Formats the value as a currency with two decimal places.
             - `"{value:.0%}"`: Formats the value as a percentage without decimal places.
             - `"{value:,}"`: Formats the value with comma as a thousands separator.

        delta_format: Format string to be applied to the headline change indicator (the bold, colored figure in the
            footer). For more details on possible placeholders, see docstring on `value_format`.
        reference_format: Format string to be applied to the supporting reference text shown next to the change
            indicator. For more details on possible placeholders, see docstring on `value_format`.
        agg_func: String function name to be used for aggregating the data. Common options include
            `"sum"`, `"mean"` or `"median"`. [More information on possible
            functions](https://stackoverflow.com/q/65877567).
        title: KPI title displayed on top of the card. If not provided, it defaults to the capitalized
            `value_column`.
        icon: Name of the icon from the [Google Material Icon Library](https://fonts.google.com/icons)
            to be displayed on the left side of the KPI title. If not provided, no icon is displayed.
        units: Unit label (for example `"%"` or `"kg"`) displayed directly after the value in a smaller,
            muted style. If not provided, no unit is displayed.
        reverse_color: If `False`, a positive delta will be colored positively (for example, blue) and a negative delta
            negatively (for example, red). If `True`, the colors will be inverted: a positive delta will be colored
            negatively (for example, red) and a negative delta positively (for example, blue).
        size: Size of the card. Possible values are `"compact"`, `"default"` or `"large"`. Defaults to `"default"`.

    Returns:
        A Dash Bootstrap Components card (`dbc.Card`) containing the formatted KPI value and reference.

    Example:
        ```python
        import vizro.models as vm
        from vizro.figures import kpi_card_reference

        vm.Figure(figure=kpi_card_reference(...))
        ```
    """
    title = title or f"{agg_func} {value_column}".title()
    value, reference = data_frame[[value_column, reference_column]].agg(agg_func)
    delta = value - reference
    delta_relative = delta / reference if reference else math.nan
    pos_color, neg_color = ("color-neg", "color-pos") if reverse_color else ("color-pos", "color-neg")
    footer_class = pos_color if delta > 0 else neg_color if delta < 0 else ""

    header = dbc.CardHeader(
        [
            html.H4(title, className="card-kpi-title"),
            html.P(validate_icon(icon), className="material-symbols-outlined") if icon else None,
        ],
        className="card-kpi-header",
    )
    body = dbc.CardBody(
        [
            value_format.format(value=value, reference=reference, delta=delta, delta_relative=delta_relative),
            html.Span(units, className="card-kpi-units") if units else None,
        ]
    )

    footer = dbc.CardFooter(
        [
            html.Span(
                [
                    html.Span(
                        "arrow_circle_up" if delta > 0 else "arrow_circle_down" if delta < 0 else "do_not_disturb_on",
                        className="material-symbols-outlined",
                    ),
                    html.Span(
                        delta_format.format(
                            value=value, reference=reference, delta=delta, delta_relative=delta_relative
                        )
                    ),
                ],
                className="card-kpi-delta-chip",
            ),
            html.Span(
                reference_format.format(value=value, reference=reference, delta=delta, delta_relative=delta_relative),
                className="card-kpi-reference-text",
            ),
        ],
        class_name=footer_class,
    )
    return dbc.Card([header, body, footer], class_name=_kpi_card_class_name(size))


def kpi_sparkline_card(  # noqa: PLR0913
    data_frame: pd.DataFrame,
    value_column: str,
    x_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: str | None = None,
    icon: str | None = None,
    units: str | None = None,
    chart_type: Literal["area", "line"] = "area",
    reverse_color: bool = False,
) -> dbc.Card:
    """Creates a styled KPI (Key Performance Indicator) card displaying a value, a trend indicator icon and a sparkline.

    !!! warning
        The format string provided to `value_format` is evaluated, so ensure that only trusted
        user input is provided to prevent potential security risks.

    Args:
        data_frame: DataFrame containing the data.
        value_column: Column name of the value to be shown.
        x_column: Column name used to order the data chronologically/sequentially. This determines both the
            x-axis of the sparkline and the trend direction shown by the indicator icon (calculated from the
            first and last values of `value_column` once sorted by `x_column`).
        value_format: Format string to be applied to the value. It must be a
            [valid Python format](https://docs.python.org/3/library/string.html#format-specification-mini-language)
            string where any of the below placeholders can be used.

            - value: `value_column` aggregated by `agg_func`.
            - delta: Difference between the last and first `value_column` entry once sorted by `x_column`.
            - delta_relative: Relative difference between the last and first `value_column` entry once sorted
                by `x_column`.

            **Common examples include:**

             - `"{value}"`: Displays the raw value.
             - `"${value:0.2f}"`: Formats the value as a currency with two decimal places.
             - `"{value:.0%}"`: Formats the value as a percentage without decimal places.
             - `"{value:,}"`: Formats the value with comma as a thousands separator.
             - `"{value} ({delta_relative:+.1%})"`: Displays the value together with its relative trend.

        agg_func: String function name to be used for aggregating the data. Common options include
            `"sum"`, `"mean"` or `"median"`. [More information on possible
            functions](https://stackoverflow.com/q/65877567).
        title: KPI title displayed on top of the card. If not provided, it defaults to the capitalized
            `value_column`.
        icon: Name of the icon from the [Google Material Icon Library](https://fonts.google.com/icons)
            to be displayed on the left side of the KPI title. If not provided, no icon is displayed.
        units: Unit label (for example `"%"` or `"kg"`) displayed directly after the value in a smaller,
            muted style. If not provided, no unit is displayed.
        chart_type: Type of sparkline chart to display, either `"area"` or `"line"`. Defaults to `"area"`. The
            sparkline itself is always rendered in the default Vizro chart color, regardless of trend direction.
        reverse_color: If `False`, an increasing trend will be indicated with a positively colored icon (for
            example, blue) and a decreasing trend with a negatively colored icon (for example, red). If `True`,
            the colors will be inverted: an increasing trend will be indicated negatively (for example, red) and
            a decreasing trend positively (for example, blue).

    Returns:
         A Dash Bootstrap Components card (`dbc.Card`) containing the formatted KPI value, a trend indicator icon
         and a sparkline chart.

    Example:
        ```python
        import vizro.models as vm
        from vizro.figures import kpi_sparkline_card

        vm.Figure(figure=kpi_sparkline_card(...))
        ```
    """
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)

    trend_df = data_frame[[x_column, value_column]].sort_values(x_column)
    trend_values = trend_df[value_column]
    delta = trend_values.iloc[-1] - trend_values.iloc[0] if len(trend_values) > 1 else 0
    delta_relative = delta / trend_values.iloc[0] if len(trend_values) > 1 and trend_values.iloc[0] else math.nan
    pos_color, neg_color = ("color-neg", "color-pos") if reverse_color else ("color-pos", "color-neg")
    delta_class = pos_color if delta > 0 else neg_color if delta < 0 else ""
    delta_icon = "arrow_circle_up" if delta > 0 else "arrow_circle_down" if delta < 0 else "arrow_circle_right"

    header = dbc.CardHeader(
        [
            html.H4(title, className="card-kpi-title"),
            html.P(validate_icon(icon), className="material-symbols-outlined") if icon else None,
        ],
        className="card-kpi-header",
    )
    body = dbc.CardBody(
        [
            html.Span(delta_icon, className=f"material-symbols-outlined {delta_class}".strip()),
            html.Span(value_format.format(value=value, delta=delta, delta_relative=delta_relative)),
            html.Span(units, className="card-kpi-units") if units else None,
        ]
    )

    sparkline_figure = go.Figure(
        go.Scatter(
            x=trend_df[x_column],
            y=trend_values,
            mode="lines",
            fill="tozeroy" if chart_type == "area" else None,
            hovertemplate="%{x}<br>%{y}<extra></extra>",
        )
    )
    sparkline_figure.update_xaxes(visible=False, showgrid=False, fixedrange=True)
    sparkline_figure.update_yaxes(visible=False, showgrid=False, fixedrange=True)
    sparkline_figure.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    footer = dbc.CardFooter(
        dcc.Graph(
            figure=sparkline_figure,
            config={"displayModeBar": False},
            className="card-kpi-sparkline-graph",
        )
    )
    return dbc.Card([header, body, footer], class_name="card-kpi card-kpi-sparkline")
