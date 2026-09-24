import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import pytest
from asserts import assert_component_equal
from dash import dcc, html

from vizro.figures import kpi_sparkline_card

# Date column deliberately unsorted to check that the trend/sparkline is computed on data sorted by x_column.
df = pd.DataFrame(
    {
        "Date": [3, 1, 2],
        "Actual": [30, 10, 20],  # sorted by Date: 10, 20, 30 -> increasing trend, sum = 60
        "Declining": [10, 30, 20],  # sorted by Date: 30, 20, 10 -> decreasing trend, sum = 60
        "Flat": [5, 5, 5],  # sorted by Date: 5, 5, 5 -> flat trend, sum = 15
        "ZeroStart": [10, 0, 5],  # sorted by Date: 0, 5, 10 -> increasing trend, first value is 0
    }
)


def _expected_sparkline_figure(value_column, chart_type):
    # Derive x/y from the module-level df (sorted by Date) rather than hardcoding Python lists, so the resulting
    # numpy arrays have the same dtype as the ones produced inside kpi_sparkline_card and thus serialize identically
    # (Plotly encodes numpy-array traces as compact binary data, which differs from plain Python list encoding).
    trend_df = df[["Date", value_column]].sort_values("Date")
    fig = go.Figure(
        go.Scatter(
            x=trend_df["Date"],
            y=trend_df[value_column],
            mode="lines",
            fill="tozeroy" if chart_type == "area" else None,
            hovertemplate="%{x}<br>%{y}<extra></extra>",
        )
    )
    fig.update_xaxes(visible=False, showgrid=False, fixedrange=True)
    fig.update_yaxes(visible=False, showgrid=False, fixedrange=True)
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _expected_card(*, header, value_text, delta_class, delta_icon, figure):
    body = dbc.CardBody(
        [
            html.Span(value_text),
            html.Span(delta_icon, className=f"material-symbols-outlined {delta_class}".strip()),
        ]
    )
    return dbc.Card(
        [
            header,
            body,
            dbc.CardFooter(
                dcc.Graph(
                    figure=figure,
                    config={"displayModeBar": False},
                    className="card-kpi-sparkline-graph",
                ),
            ),
        ],
        class_name="card-kpi card-kpi-sparkline",
    )


class TestKPISparklineCard:
    def test_kpi_sparkline_card_mandatory_increasing(self):
        result = kpi_sparkline_card(data_frame=df, value_column="Actual", x_column="Date")()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
            value_text="60",
            delta_class="color-pos",
            delta_icon="arrow_circle_up",
            figure=_expected_sparkline_figure("Actual", "area"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_mandatory_decreasing(self):
        result = kpi_sparkline_card(data_frame=df, value_column="Declining", x_column="Date")()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Declining", className="card-kpi-title")]),
            value_text="60",
            delta_class="color-neg",
            delta_icon="arrow_circle_down",
            figure=_expected_sparkline_figure("Declining", "area"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_mandatory_flat(self):
        result = kpi_sparkline_card(data_frame=df, value_column="Flat", x_column="Date")()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Flat", className="card-kpi-title")]),
            value_text="15",
            delta_class="",
            delta_icon="arrow_circle_right",
            figure=_expected_sparkline_figure("Flat", "area"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_reverse_color(self):
        result = kpi_sparkline_card(data_frame=df, value_column="Actual", x_column="Date", reverse_color=True)()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
            value_text="60",
            delta_class="color-neg",
            delta_icon="arrow_circle_up",
            figure=_expected_sparkline_figure("Actual", "area"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_chart_type_line(self):
        result = kpi_sparkline_card(data_frame=df, value_column="Actual", x_column="Date", chart_type="line")()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Actual", className="card-kpi-title")]),
            value_text="60",
            delta_class="color-pos",
            delta_icon="arrow_circle_up",
            figure=_expected_sparkline_figure("Actual", "line"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_mandatory_and_optional(self):
        result = kpi_sparkline_card(
            data_frame=df,
            value_column="Actual",
            x_column="Date",
            icon="Shopping Cart",
            title="sales",
            value_format="${value:0.2f} ({delta_relative:+.1%})",
            agg_func="mean",
        )()
        expected = _expected_card(
            header=dbc.CardHeader(
                [
                    html.P("shopping_cart", className="material-symbols-outlined"),
                    html.H4("sales", className="card-kpi-title"),
                ]
            ),
            value_text="$20.00 (+200.0%)",
            delta_class="color-pos",
            delta_icon="arrow_circle_up",
            figure=_expected_sparkline_figure("Actual", "area"),
        )
        assert_component_equal(result, expected)

    def test_kpi_sparkline_card_zero_start(self):
        result = kpi_sparkline_card(
            data_frame=df, value_column="ZeroStart", x_column="Date", value_format="{value} ({delta_relative:+.1%})"
        )()
        expected = _expected_card(
            header=dbc.CardHeader([None, html.H4("Sum Zerostart", className="card-kpi-title")]),
            value_text="15 (+nan%)",
            delta_class="color-pos",
            delta_icon="arrow_circle_up",
            figure=_expected_sparkline_figure("ZeroStart", "area"),
        )
        assert_component_equal(result, expected)

    def test_value_format_missing_placeholder(self):
        with pytest.raises(
            IndexError,
            match="Replacement index 0 out of range for positional args tuple",
        ):
            kpi_sparkline_card(data_frame=df, value_column="Actual", x_column="Date", value_format="{.2f}}")()

    def test_value_format_nonexisting_placeholder(self):
        with pytest.raises(KeyError, match="reference"):
            kpi_sparkline_card(data_frame=df, value_column="Actual", x_column="Date", value_format="{reference.2f}}")()
