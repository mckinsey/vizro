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
                html.H4(self.title),
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
def bar(
    x: str,
    y: str,
    data_frame: pd.DataFrame,
    top_n: int = 15,
    custom_data: Optional[List[str]] = None,
):
    df_agg = data_frame.groupby(y).agg({x: "count"}).sort_values(by=x, ascending=False).reset_index()

    fig = px.bar(
        data_frame=df_agg.head(top_n),
        x=x,
        y=y,
        orientation="h",
        text=x,
        color_discrete_sequence=["#1A85FF"],
        custom_data=custom_data,
    )
    fig.update_layout(xaxis_title="# of Complaints", yaxis=dict(title="", autorange="reversed"))  # noqa: C408
    return fig


@capture("graph")
def line(x: str, y: str, data_frame: pd.DataFrame):
    df_agg = data_frame.groupby(x).agg({y: "count"}).reset_index()
    fig = px.area(
        data_frame=df_agg,
        x=x,
        y=y,
        color_discrete_sequence=["#1A85FF"],
        title="Complaints over time",
    )
    fig.update_layout(xaxis_title="Date Received", yaxis_title="# of Complaints", title_pad_t=4)
    return fig


@capture("graph")
def pie(
    names: str,
    values: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
    custom_order: Optional[List[str]] = None,
):
    df_agg = data_frame.groupby(names).agg({values: "count"}).reset_index()

    # Apply custom order so colors are applied correctly to the pie chart
    order_mapping = {category: index for index, category in enumerate(custom_order)}
    df_sorted = df_agg.sort_values(by=names, key=lambda names: names.map(order_mapping))

    fig = px.pie(
        data_frame=df_sorted,
        names=names,
        values=values,
        color_discrete_sequence=["#1a85ff", "#7ea1ee", "#adbedc", "#df658c", "#d41159"],
        title=title,
        hole=0.4,
    )

    fig.update_layout(legend_x=1, legend_y=1, title_pad_t=2, margin=dict(l=0, r=0, t=60, b=0))  # noqa: C408
    fig.update_traces(sort=False)
    return fig


@capture("graph")
def choropleth(
    locations: str,
    color: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
    custom_data: Optional[List[str]] = None,
):
    df_agg = data_frame.groupby(locations).agg({color: "count"}).reset_index()

    fig = px.choropleth(
        data_frame=df_agg,
        locations=locations,
        color=color,
        color_continuous_scale=[
            "#ded6d8",
            "#f3bdcb",
            "#f7a9be",
            "#f894b1",
            "#f780a3",
            "#f46b94",
            "#ee517f",
            "#e94777",
            "#e43d70",
            "#df3168",
            "#d92460",
            "#d41159",
        ],
        scope="usa",
        locationmode="USA-states",
        title=title,
        custom_data=custom_data,
    )

    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig


# TABLE CONFIGURATIONS ---------------------------------------------------------
CELL_STYLE = {
    "styleConditions": [
        {
            "condition": "params.value == 'Closed with explanation'",
            "style": {"backgroundColor": "#1a85ff"},
        },
        {
            "condition": "params.value == 'Closed with monetary relief'",
            "style": {"backgroundColor": "#d41159"},
        },
        {
            "condition": "params.value == 'Closed with non-monetary relief'",
            "style": {"backgroundColor": "#adbedc"},
        },
        {
            "condition": "params.value == 'Closed without relief'",
            "style": {"backgroundColor": "#7ea1ee"},
        },
        {
            "condition": "params.value == 'Closed with relief'",
            "style": {"backgroundColor": "#df658c"},
        },
        {
            "condition": "params.value == 'Closed'",
            "style": {"backgroundColor": "#1a85ff"},
        },
    ]
}


COLUMN_DEFS = [
    {"field": "Complaint ID", "cellDataType": "text", "headerName": "ID", "flex": 3},
    {"field": "Date Received", "cellDataType": "text", "headerName": "Date", "flex": 3},
    {"field": "Channel", "cellDataType": "text", "flex": 3},
    {"field": "State", "cellDataType": "text", "flex": 2},
    {"field": "Product", "cellDataType": "text", "flex": 5},
    {"field": "Issue", "cellDataType": "text", "flex": 5},
    {
        "field": "Company response - detailed",
        "cellDataType": "text",
        "cellStyle": CELL_STYLE,
        "headerName": "Company response",
        "flex": 6,
    },
    {"field": "Timely response?", "cellRenderer": "markdown", "headerName": "On time?", "flex": 3},
]
