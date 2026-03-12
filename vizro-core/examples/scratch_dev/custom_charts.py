import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from dash import html
from dash_ag_grid import AgGrid
from data import daily_baseline
from vizro.models._models_utils import validate_icon
from vizro.models.types import capture


@capture("ag_grid")
def scenarios_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid with a 'Scenario action' column containing a button per row."""
    column_defs = []
    for col in data_frame.columns:
        column_defs.append({"field": col})

    dashGridOptions = {
        "animateRows": False,
        "domLayout": "autoHeight",
        "pagination": True,
        "paginationPageSize": 10,
        "theme": {"function": "vizroTheme(themeQuartz, agGrid)"},
        "rowSelection": {"mode": "singleRow"},
    }
    return AgGrid(
        columnDefs=column_defs,
        rowData=data_frame.to_dict("records"),
        dashGridOptions=dashGridOptions,
        columnSize="responsiveSizeToFit",
        **kwargs,
    )


@capture("figure")
def custom_kpi_card_reference(
    data_frame=None,
    data_frame_reference=None,
    *,
    value_column: str = "value",
    reference_column: str = "reference",
    value_format: str = "{value}",
    reference_format: str = "{delta_relative:+.1%} vs. reference ({reference})",
    agg_func: str = "sum",
    title: str | None = None,
    icon: str | None = None,
    reverse_color: bool = False,
):
    """KPI card comparing a scenario value to a baseline reference from two separate dataframes.

    Value is taken from data_frame[value_column] (aggregated by agg_func).
    Reference is taken from data_frame_reference[reference_column] (aggregated by agg_func).

    Placeholders for format strings: value, reference, delta, delta_relative.
    """
    value = (
        data_frame[value_column].agg(agg_func)
        if data_frame is not None and not data_frame.empty and value_column in data_frame.columns
        else np.nan
    )
    reference = (
        data_frame_reference[reference_column].agg(agg_func)
        if data_frame_reference is not None
        and not data_frame_reference.empty
        and reference_column in data_frame_reference.columns
        else np.nan
    )
    delta = value - reference
    delta_relative = delta / reference if reference and reference != 0 else np.nan
    pos_color, neg_color = ("color-neg", "color-pos") if reverse_color else ("color-pos", "color-neg")
    footer_class = pos_color if delta > 0 else neg_color if delta < 0 else ""

    display_title = title or f"{agg_func} {value_column}".title()
    header = dbc.CardHeader(
        [
            html.P(validate_icon(icon), className="material-symbols-outlined") if icon else None,
            html.H4(display_title, className="card-kpi-title"),
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
        className=footer_class,
    )
    return dbc.Card([header, body, footer], className="card-kpi", style={"overflow": "hidden"})


_METRIC_CONFIG = {
    "total_production_volume_ton": {"title": "Total production volume", "y_label": "ton"},
    "daily_avg_wip_ton": {"title": "Daily average WIP", "y_label": "ton"},
}
_DEFAULT_METRIC_CONFIG = {"title": "Average lead time", "y_label": "ton"}


@capture("graph")
def plot_total_production_volume(data_frame, metric):
    """Line chart of a single metric over time for one scenario."""
    config = _METRIC_CONFIG.get(metric, _DEFAULT_METRIC_CONFIG)
    scenario_name = data_frame["scenario_name"].iloc[0] if not data_frame.empty else ""

    fig = px.line(
        data_frame,
        x="date_label",
        y=metric,
        markers=True,
        labels={"date_label": "", metric: config["y_label"]},
        title=f"{config['title']} - {scenario_name}",
    )
    return fig


@capture("graph")
def plot_comparison_total_production_volume(
    data_frame=None,
    data_frame_scenario_2=None,
    *,
    scenario_1_label: str = "Baseline",
    scenario_2_label: str = "Scenario a",
    value_column: str = "ton",
    date_label_column: str = "date_label",
):
    """Line chart comparing two scenarios from two datasets.

    Uses two separate datasets: data_frame_scenario_1 (e.g. Baseline) and
    data_frame_scenario_2 (e.g. Scenario a). Each dataframe should have
    date_label_column and value_column.
    """
    if data_frame is None or data_frame.empty:
        data_frame = pd.DataFrame()
    if data_frame_scenario_2 is None or data_frame_scenario_2.empty:
        data_frame_scenario_2 = daily_baseline

    fig = go.Figure()
    # Baseline: dotted line with markers (neutral color for light/dark theme)
    fig.add_trace(
        go.Scatter(
            x=data_frame[date_label_column],
            y=data_frame[value_column],
            mode="lines+markers",
            name=scenario_1_label,
            line=dict(color="#6d6f77", width=2, dash="dot"),
            marker=dict(size=8, symbol="circle"),
        )
    )
    # Scenario a: solid teal line with markers
    fig.add_trace(
        go.Scatter(
            x=data_frame_scenario_2[date_label_column],
            y=data_frame_scenario_2[value_column],
            mode="lines+markers",
            name=scenario_2_label,
            line=dict(color="rgb(8, 189, 186)", width=2, dash="solid"),  # teal
            marker=dict(size=8, symbol="circle"),
        )
    )
    fig.update_layout(
        xaxis=dict(
            title="",
            tickformat="",
            gridcolor="rgba(255,255,255,0.08)",
        ),
        yaxis=dict(
            title=value_column,
            range=[40, 70],
            gridcolor="rgba(255,255,255,0.08)",
        ),
        hovermode="x unified",
    )
    return fig
