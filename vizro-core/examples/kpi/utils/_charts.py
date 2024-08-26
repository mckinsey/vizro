"""Contains custom components and charts used inside the dashboard."""

from typing import List, Literal, Optional

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro.models.types import capture


# CUSTOM COMPONENTS -------------------------------------------------------------
class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"
    title: str = None  # Title exists in vm.Container but we don't want to use it here.
    classname: str = "d-flex"

    def build(self):
        """Returns a flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className=self.classname
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
    """Custom bar chart implementation.

    Based on [px.bar](https://plotly.com/python-api-reference/generated/plotly.express.bar).
    """
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
    fig.update_layout(xaxis_title="# of Complaints", yaxis={"title": "", "autorange": "reversed"})
    return fig


@capture("graph")
def area(x: str, y: str, data_frame: pd.DataFrame):
    """Custom chart to create unstacked area chart.

    Based on [go.Scatter](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html).

    """
    df_agg = data_frame.groupby(["Year", "Month"]).agg({y: "count"}).reset_index()
    df_agg_2019 = df_agg[df_agg["Year"] == "2018"]
    df_agg_2020 = df_agg[df_agg["Year"] == "2019"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df_agg_2020[x], y=df_agg_2020[y], fill="tozeroy", name="2019", marker={"color": "#1a85ff"})
    )
    fig.add_trace(go.Scatter(x=df_agg_2019[x], y=df_agg_2019[y], fill="tonexty", name="2018", marker={"color": "grey"}))
    fig.update_layout(
        title="Complaints over time",
        xaxis_title="Date Received",
        yaxis_title="# of Complaints",
        title_pad_t=4,
        xaxis={
            "showgrid": False,
            "tickmode": "array",
            "tickvals": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "ticktext": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        },
    )
    return fig


@capture("graph")
def pie(
    names: str,
    values: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
):
    """Custom pie chart implementation.

    Based on [px.pie](https://plotly.com/python-api-reference/generated/plotly.express.pie).
    """
    df_agg = data_frame.groupby(names).agg({values: "count"}).reset_index()
    fig = px.pie(
        data_frame=df_agg,
        names=names,
        values=values,
        color=names,
        color_discrete_map={
            "Closed with explanation": "#1a85ff",
            "Closed with monetary relief": "#d41159",
            "Closed with non-monetary relief": "#adbedc",
            "Closed without relief": "#7ea1ee",
            "Closed with relief": "#df658c",
            "Closed": "#1a85ff",
        },
        title=title,
        hole=0.4,
    )
    fig.update_layout(legend_x=1, legend_y=1, title_pad_t=2, margin={"l": 0, "r": 0, "t": 60, "b": 0})
    return fig


@capture("graph")
def choropleth(
    locations: str,
    color: str,
    data_frame: pd.DataFrame = None,
    title: Optional[str] = None,
    custom_data: Optional[List[str]] = None,
):
    """Custom choropleth implementation.

    Based on [px.choropleth](https://plotly.com/python-api-reference/generated/plotly.express.choropleth).
    """
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
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "bottom"}, "orientation": "h", "x": 0.5, "y": 0})
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
