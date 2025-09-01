"""Collection of custom charts."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def custom_scatter(data_frame: pd.DataFrame, x: str, y: str):
    """Custom scatter plot."""
    return go.Figure(data=[go.Scatter(x=data_frame[x], y=data_frame[y])])


@capture("graph")
def custom_bar(data_frame: pd.DataFrame):
    """Custom bar plot."""

    # Create base figure
    fig = go.Figure()

    # Add 2024 Revenue bars
    fig.add_trace(go.Bar(
        y=data_frame["Industry"],
        x=data_frame["2024_Revenue"],
        name="2024 Revenue",
        orientation="h",
        marker=dict(color="gold"),
        text=data_frame["2024_Revenue"].astype(str) + "M",
        textposition="inside"
    ))

    # Add Opportunity bars stacked
    fig.add_trace(go.Bar(
        y=data_frame["Industry"],
        x=data_frame["Opportunity"],
        name="Opportunity",
        orientation="h",
        marker=dict(color="royalblue"),
        text=data_frame["Opportunity"].astype(str) + "M",
        textposition="inside"
    ))

    # Add total labels at the end of bars
    for i, row in data_frame.iterrows():
        fig.add_annotation(x=row["Total"] + 2,  # a bit offset to the right
                           y=row["Industry"],
                           text=f"{row['Total']}M",
                           showarrow=False,
                           font=dict(color="white", size=12))

    # Layout updates
    fig.update_layout(
        title="Serviceable Addressable Market by Industry Vertical",
        barmode="stack",
        xaxis=dict(title="", showgrid=False, zeroline=False),
        yaxis=dict(title="", categoryorder="total ascending"),
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
    )

    return fig


def custom_bar_2():
    pass
