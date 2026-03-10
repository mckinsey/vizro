"""Dev app to try things out."""

import json
import vizro.models as vm
from typing import Literal
from dash import dcc, Input, Output, callback, Patch
from dash_ag_grid import AgGrid

from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.figures import kpi_card, kpi_card_reference
import plotly.graph_objects as go
import vizro.plotly.express as px
from dash import html

from data import (
    scenario_data,
    wip_waterfall,
    wip_by_equipment,
    kpi_summary_production,
    kpi_summary_lead,
    kpi_summary_average,
    daily_data,
    kpis_per_product_type,
    kpi_comparison_production,
    kpi_comparison_avg_lead,
    kpi_comparison_avg,
    daily_baseline,
    daily_scenario_a,
)


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
        "rowSelection": {"mode": "multiRow"},
    }
    return AgGrid(
        columnDefs=column_defs,
        rowData=data_frame.to_dict("records"),
        dashGridOptions=dashGridOptions,
        columnSize="responsiveSizeToFit",
        **kwargs,
    )


def _format_kpi_value(value):
    """Format number with thousands separator and 2 decimal places."""
    if value is None or (isinstance(value, float) and (value != value)):  # NaN
        return "—"
    return f"{float(value):,.2f}"


@capture("figure")
def kpi_card_actual_vs_scenarios(
    data_frame=None,
    *,
    title: str = "KPI",
    actual_column: str = "actual",
    scenario_1_column: str = "scenario_1",
    scenario_2_column: str = "scenario_2",
    scenario_1_label: str = "Baseline",
    scenario_2_label: str = "Scenario A",
    unit: str = "ton",
):
    """Custom KPI card showing Actual, Scenario 1 and Scenario 2 values with colored bullets.

    Expects data_frame with one row and columns for actual, scenario_1, scenario_2 (or pass column names).
    Alternatively pass a dict-like row with keys actual_column, scenario_1_column, scenario_2_column.
    """
    import dash_bootstrap_components as dbc

    if data_frame is not None and not data_frame.empty:
        row = data_frame.iloc[0]
        actual_value = row.get(actual_column) if actual_column in row else row.get("actual")
        scenario_1_value = (
            row.get(scenario_1_column)
            if scenario_1_column in row
            else row.get("scenario_1") or row.get("baseline_value")
        )
        scenario_2_value = row.get(scenario_2_column) if scenario_2_column in row else row.get("scenario_2")
        if "unit" in row and row.get("unit"):
            unit = str(row["unit"])
    else:
        actual_value = scenario_1_value = scenario_2_value = None

    title_el = html.Div(
        [html.H4(title, className="card-kpi-title")],
    )

    def make_row(label: str, value):
        return html.Div(html.Span(f"{label}: {value} {unit}"))

    rows = [
        make_row("Actual", actual_value),
        make_row(scenario_1_label, scenario_1_value),
        make_row(scenario_2_label, scenario_2_value),
    ]
    body = html.Div([title_el, html.Div(rows)], style={"padding": "1rem"}, className="card-kpi-body")

    return dbc.Card(body, className="card-kpi", style={"overflow": "hidden"})


@capture("graph")
def plot_total_production_volume(data_frame):
    fig = px.line(
        data_frame,
        x="date_label",
        y="total_production_volume_ton",
        markers=True,
        labels={"date_label": "", "total_production_volume_ton": "ton"},
        title="Total production volume",
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
        data_frame = daily_baseline
    if data_frame_scenario_2 is None or data_frame_scenario_2.empty:
        data_frame_scenario_2 = daily_scenario_a

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


page_1 = vm.Page(
    title="SCENARIO ANALYSIS TOOL",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="List of Scenarios",
                    components=[
                        vm.AgGrid(figure=scenarios_ag_grid(data_frame=scenario_data, id="custom_ag_grid")),
                        vm.Button(text="Compare", id="compare-btn"),
                    ],
                    controls=[
                        vm.Filter(
                            column="baseline",
                            selector=vm.Checklist(
                                options=[{"label": "True", "value": True}, {"label": "False", "value": False}]
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Comparison View",
                    components=[
                        vm.Figure(
                            figure=kpi_card_actual_vs_scenarios(
                                data_frame=kpi_comparison_production,
                                title="The total production volume",
                                actual_column="actual",
                                scenario_1_column="scenario_1",
                                scenario_2_column="scenario_2",
                                scenario_1_label="Baseline",
                                scenario_2_label="Scenario A",
                                unit="ton",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_actual_vs_scenarios(
                                data_frame=kpi_comparison_avg,
                                title="The total production volume",
                                actual_column="actual",
                                scenario_1_column="scenario_1",
                                scenario_2_column="scenario_2",
                                scenario_1_label="Baseline",
                                scenario_2_label="Scenario A",
                                unit="ton",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_actual_vs_scenarios(
                                data_frame=kpi_comparison_avg_lead,
                                title="The total production volume",
                                actual_column="actual",
                                scenario_1_column="scenario_1",
                                scenario_2_column="scenario_2",
                                scenario_1_label="Baseline",
                                scenario_2_label="Scenario A",
                                unit="ton",
                            )
                        ),
                        vm.Tabs(
                            tabs=[
                                vm.Container(
                                    title="Total production volume",
                                    components=[
                                        vm.Graph(
                                            figure=plot_comparison_total_production_volume(
                                                data_frame=daily_baseline,
                                                data_frame_scenario_2=daily_scenario_a,
                                                scenario_1_label="Baseline",
                                                scenario_2_label="Scenario a",
                                                value_column="ton",
                                                date_label_column="date_label",
                                            )
                                        ),
                                    ],
                                )
                            ]
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 3, 3, 3],
                            [1, 3, 3, 3],
                            [2, 3, 3, 3],
                        ]
                    ),
                ),
            ]
        )
    ],
    # controls=[
    #     vm.Parameter(
    #         target=""
    #     )
    # ]
)


page_2 = vm.Page(
    title="Scenario details",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="KPIs",
                    components=[
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_production,
                                value_column="value",
                                reference_column="baseline_value",
                                title="The total production volume",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_average,
                                value_column="value",
                                reference_column="baseline_value",
                                title="Daily average WIP",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card_reference(
                                data_frame=kpi_summary_lead,
                                value_column="value",
                                reference_column="baseline_value",
                                title="Average lead time",
                            )
                        ),
                        vm.Tabs(
                            tabs=[
                                vm.Container(
                                    title="Total production volume",
                                    components=[vm.Graph(figure=plot_total_production_volume(daily_data))],
                                ),
                                vm.Container(title="WIP by equipment", components=[vm.Card(text="placeholder")]),
                                vm.Container(title="WIP waterfall", components=[vm.Card(text="placeholder")]),
                            ]
                        ),
                        vm.Container(
                            title="KPI per product type",
                            components=[
                                vm.AgGrid(figure=dash_ag_grid(kpis_per_product_type)),
                            ],
                            layout=vm.Flex(),
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 3, 3, 3],
                            [1, 3, 3, 3],
                            [2, 3, 3, 3],
                            [4, 4, 4, 4],
                            [4, 4, 4, 4],
                            [4, 4, 4, 4],
                        ],
                        row_min_height="150px",
                    ),
                ),
                vm.Container(title="Gun-kan chart", components=[vm.Card(text="placeholder")]),
                vm.Container(title="Gun-kan chart - detailed", components=[vm.Card(text="placeholder")]),
            ]
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1, page_2],
    title="QB",
)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
