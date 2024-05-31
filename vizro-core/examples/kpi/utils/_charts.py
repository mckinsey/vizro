"""Contains custom components and charts used inside the dashboard."""

from typing import List, Literal, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro.models.types import capture


# CUSTOM COMPONENTS -------------------------------------------------------------
# Note: This is a static KPI Card only (it will not be reactive to controls). A new dynamic KPI Card component
# is currently in development.
class KPI(vm.VizroBaseModel):
    """Static custom `KPI` Card."""

    type: Literal["kpi"] = "kpi"
    title: str
    value: str
    icon: str
    sign: Literal["delta-pos", "delta-neg"]
    ref_value: str

    def build(self):
        return dbc.Card(
            [
                html.H2(self.title),
                html.P(self.value),
                html.Span(
                    [
                        html.Span(self.icon, className="material-symbols-outlined"),
                        html.Span(self.ref_value),
                    ],
                    className=self.sign,
                ),
            ],
            className="kpi-card-ref",
        )


# CUSTOM CHARTS ----------------------------------------------------------------
@capture("graph")
def bar(x: str, y: str, data_frame: pd.DataFrame = None, top_n: int = 15, color_discrete_sequence: List[str] = None):
    df_agg = data_frame.groupby([y]).aggregate({x: "count"}).sort_values(by=x, ascending=False).reset_index()

    fig = px.bar(
        data_frame=df_agg.head(top_n),
        x=x,
        y=y,
        orientation="h",
        text=x,
        color_discrete_sequence=color_discrete_sequence,
    )
    fig.update_layout(xaxis_title="# of Complaints", yaxis=dict(title="", autorange="reversed"))
    return fig


@capture("graph")
def line(x: str, y: str, data_frame: pd.DataFrame = None, color_discrete_sequence: List[str] = None):
    df_agg = data_frame.groupby([x]).aggregate({y: "count"}).reset_index()
    fig = px.area(
        data_frame=df_agg,
        x=x,
        y=y,
        color_discrete_sequence=color_discrete_sequence,
        title="Complaints over time - monthly",
    )
    fig.update_layout(xaxis_title="Date Received", yaxis_title="# of Complaints", title_pad_t=4)
    return fig


@capture("graph")
def pie(
    names: str,
    values: str,
    data_frame: pd.DataFrame = None,
    color_discrete_sequence: List[str] = None,
    title: Optional[str] = None,
):
    df_agg = data_frame.groupby([names]).aggregate({values: "count"}).reset_index()

    fig = px.pie(
        data_frame=df_agg,
        names=names,
        values=values,
        color_discrete_sequence=color_discrete_sequence,
        title=title,
        hole=0.4,
    )

    fig.update_layout(legend_x=1, legend_y=1, title_pad_t=4, margin=dict(l=0, r=24, t=40, b=16))
    return fig


@capture("graph")
def chloropleth(locations: str, color: str, data_frame: pd.DataFrame = None):

    df_agg = data_frame.groupby([locations]).aggregate({color: "count"}).reset_index()
    df_agg = df_agg[~df_agg["State"].isin(["N/A", "UNITED STATES MINOR OUTLYING ISLANDS"])]

    fig = px.choropleth(
        data_frame=df_agg,
        locations=locations,
        color=color,
        #    color_continuous_scale=["#d41159", "#d41159", "#d41159", "#d3d3d3", "#1a85ff", "#1a85ff", "#1a85ff"],
        scope="usa",
        locationmode="USA-states",
    )

    #   fig.update_layout(title_text="Change in revenue by ZIP code", margin=dict(l=0, r=0, t=0), title_pad_t=20)
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig


# TABLE CONFIGURATIONS ---------------------------------------------------------
CELL_STYLE = {
    "styleConditions": [
        {
            "condition": "params.value == 'Closed with explanation'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with monetary relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with non-monetary relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed without relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed with relief'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'Closed'",
            "style": {"backgroundColor": "#78a9ff"},
        },
        {
            "condition": "params.value == 'In progress'",
            "style": {"backgroundColor": "orange"},
        },
        {
            "condition": "params.value == 'Untimely response'",
            "style": {"backgroundColor": "#D41159"},
        },
    ]
}


COLUMN_DEFS = [
    {"field": "Complaint ID", "cellDataType": "text", "headerName": "ID", "flex": 1},
    {"field": "Date Received", "cellDataType": "text", "flex": 2},
    {"field": "Channel", "cellDataType": "text", "flex": 1},
    {"field": "State", "cellDataType": "text", "flex": 1},
    {"field": "Product", "cellDataType": "text", "flex": 3},
    {"field": "Issue", "cellDataType": "text", "flex": 3},
    {
        "field": "Company response - detailed",
        "cellDataType": "text",
        "cellStyle": CELL_STYLE,
        "headerName": "Company response",
        "flex": 3
    },
    {"field": "Timely response?", "cellRenderer": "markdown", "headerName": "Timely", "flex": 1},
]
