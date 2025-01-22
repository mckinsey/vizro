"""Custom charts."""

from datetime import datetime

import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def custom_polar(data_frame):
    avg_empathy = data_frame["Empathy"].mean()
    avg_professionalism = data_frame["Professionalism"].mean()
    avg_communication = data_frame["Effective Communication"].mean()
    avg_listening = data_frame["Active Listening"].mean()
    avg_kindness = data_frame["Kindness"].mean()

    radar_data = pd.DataFrame(
        {
            "Quality": [
                "Empathy",
                "Professionalism",
                "Effective Communication",
                "Active Listening",
                "Kindness",
            ],
            "Average": [
                avg_empathy,
                avg_professionalism,
                avg_communication,
                avg_listening,
                avg_kindness,
            ],
        }
    )

    fig = px.line_polar(
        radar_data,
        r="Average",
        theta="Quality",
        line_close=True,
        line_shape="spline",
        range_r=[0, 5],
    )
    fig.update_traces(fill="toself")

    return fig


@capture("graph")
def custom_pie_chart_upsale(data_frame):
    upsale_outcomes = data_frame.groupby(["Upsale Attempted", "Upsale Success"]).size().reset_index(name="counts")

    def categorize(row):
        if not row["Upsale Attempted"]:
            return "No upsale Attempted"
        elif row["Upsale Success"]:
            return "Successful upsales"
        else:
            return "Failed Upsales"

    upsale_outcomes["category"] = upsale_outcomes.apply(categorize, axis=1)
    category_counts = upsale_outcomes.groupby("category")["counts"].sum().reset_index()

    fig = px.pie(
        category_counts,
        values="counts",
        names="category",
        hole=0.6,
        labels={"counts": "Number of Calls"},
    )
    fig.update_layout(margin_t=0, margin_b=0)
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        opacity=0.9,
    )
    fig.update_layout(showlegend=False)
    return fig


@capture("graph")
def custom_pie_chart_concern(data_frame):
    counts = data_frame["Concern Addressed"].value_counts()
    labels = ["Concerns not addressed", "Concerns addressed"]

    chart_data = pd.DataFrame({"Labels": labels, "Counts": [counts.get(False, 0), counts.get(True, 0)]})

    fig = px.pie(
        chart_data,
        values="Counts",
        names="Labels",
        hole=0.6,
        color="Labels",
        color_discrete_map={"Concerns addressed": "#00b4ff", "Concerns not addressed": "#ff9222"},
    )
    fig.update_layout(margin_t=0, margin_b=0)
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        opacity=0.9,
    )
    fig.update_layout(showlegend=False)
    return fig


@capture("graph")
def custom_heatmap(data_frame):
    data_frame["Call Date"] = pd.to_datetime(data_frame["Call Date"])
    data_frame["Time"] = pd.to_datetime(data_frame["Time"])
    data_frame["Time"] = data_frame["Time"].dt.time
    reference_date = datetime(2023, 1, 1)
    data_frame["Time"] = data_frame["Time"].apply(lambda t: datetime.combine(reference_date, t))
    data_frame["Time"] = data_frame["Time"].dt.floor("1H")

    result = (
        data_frame.groupby(["Time", "Call Date"])
        .apply(lambda group: (group["Concern Addressed"].sum() * 100))
        .reset_index(name="Concern Addressed")
    )
    result["Call Date"] = data_frame["Call Date"]

    fig = px.density_heatmap(
        result,
        x="Time",
        y="Call Date",
        z="Concern Addressed",
        histfunc="avg",
        text_auto=".2f",
        range_color=[0, 100],
        # color_continuous_scale=["#00b4ff", "#ff9222"],
    )
    fig.update_layout(xaxis=dict(range=["2023-01-01 08:00", "2023-01-01 18:00"]))
    fig.update_layout(
        xaxis=dict(
            tickvals=[
                "2023-01-01 08:00",
                "2023-01-01 09:00",
                "2023-01-01 10:00",
                "2023-01-01 11:00",
                "2023-01-01 12:00",
                "2023-01-01 13:00",
                "2023-01-01 14:00",
                "2023-01-01 15:00",
                "2023-01-01 16:00",
                "2023-01-01 17:00",
                "2023-01-01 18:00",
            ],
            ticktext=[
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
            ],
        )
    )
    return fig


@capture("graph")
def custom_scatter_chart(data_frame):
    summary_data = (
        data_frame.groupby(["Agent Tone", "Client Tone"])
        .agg(Total=("Concern Addressed", "count"), Addressed=("Concern Addressed", "sum"))
        .reset_index()
    )
    summary_data["% Concerns Addressed"] = (summary_data["Addressed"] / summary_data["Total"]) * 100

    fig = px.scatter(
        summary_data,
        x="Agent Tone",
        y="Client Tone",
        size="Total",
        color="% Concerns Addressed",
        range_color=[0, 100],
        # color_continuous_scale=["#00b4ff", "#ff9222"],
        labels={"% Concerns Addressed": "% Concerns Addressed"},
    )
    return fig


def custom_map_chart(data_frame):
    aggregated_df = (
        data_frame.groupby(["Caller City", "latitude", "longitude"])
        .agg(
            Call_Count=("Caller ID", "count"),
            Agent_IDs=("Agent ID", "count"),
        )
        .reset_index()
    )

    merged_df = data_frame.merge(aggregated_df, on=["Caller City", "latitude", "longitude"], how="left")

    fig = px.scatter_mapbox(
        merged_df,
        lat="latitude",
        lon="longitude",
        size="Call_Count",
        mapbox_style="carto-positron",
        hover_name="Caller City",
        hover_data={
            "Call_Count": True,
            "Agent_IDs": True,
        },
        zoom=3,
    )
    fig.update_layout(showlegend=False)

    return fig


@capture("graph")
def custom_box_chart(data_frame):
    fig = px.box(
        data_frame,
        x="Agent ID",
        y="Effective Communication",
        labels={
            "Effective Communication": "Effective Communication Score",
            "Agent ID": "Agent ID",
        },
    )
    return fig
