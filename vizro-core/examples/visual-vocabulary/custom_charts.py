"""Contains custom charts used inside the dashboard."""

from typing import List

import pandas as pd
import vizro.plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from vizro.models.types import capture


# TODO: consider how this should be represented in the code example files. Since the code is copy and pasted
# it can get out of sync. But probably we don't want the docstrings in the short code snippet.
# Ultimately these charts will probably move to vizro.charts anyway.
@capture("graph")
def butterfly(data_frame: pd.DataFrame, x1: str, x2: str, y: str) -> go.Figure:
    """Creates a custom butterfly chart using Plotly's go.Figure.

    A butterfly chart is a type of bar chart where two sets of bars are displayed back-to-back, often used to compare
    two sets of data.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x1 (str): The name of the column in the data frame for the first set of bars (negative values).
        x2 (str): The name of the column in the data frame for the second set of bars (positive values).
        y (str): The name of the column in the data frame for the y-axis (categories).

    Returns:
        go.Figure: A Plotly Figure object representing the butterfly chart.

    """
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=-data_frame[x1],
            y=data_frame[y],
            orientation="h",
            name=x1,
        )
    )
    fig.add_trace(
        go.Bar(
            x=data_frame[x2],
            y=data_frame[y],
            orientation="h",
            name=x2,
        )
    )
    fig.update_layout(barmode="relative")
    return fig


@capture("graph")
def sankey(data_frame: pd.DataFrame, source: str, target: str, value: str, labels: List[str]) -> go.Figure:
    """Creates a custom sankey chart using Plotly's `go.Sankey`.

    A Sankey chart is a type of flow diagram where the width of the arrows is proportional to the flow rate.
    It is used to visualize the flow of resources or data between different stages or categories.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        source (str): The name of the column in the data frame for the source nodes.
        target (str): The name of the column in the data frame for the target nodes.
        value (str): The name of the column in the data frame for the values representing the flow between nodes.
        labels (List[str]): A list of labels for the nodes.

    Returns:
        go.Figure: A Plotly Figure object representing the Sankey chart.

    For detailed information on additional parameters and customization, refer to the Plotly documentation:
    https://plotly.com/python/reference/sankey/

    """
    fig = go.Figure(
        data=[
            go.Sankey(
                node={
                    "pad": 16,
                    "thickness": 16,
                    "label": labels,
                },
                link={
                    "source": data_frame[source],
                    "target": data_frame[target],
                    "value": data_frame[value],
                    "label": labels,
                    "color": "rgba(205, 209, 228, 0.4)",
                },
            )
        ]
    )
    fig.update_layout(barmode="relative")
    return fig


@capture("graph")
def column_and_line(data_frame: pd.DataFrame, x: str, y_column: str, y_line: str) -> go.Figure:
    """Creates a combined column and line chart using Plotly.

    This function generates a chart with a bar graph for one variable (y-axis 1) and a line graph for another variable
    (y-axis 2), sharing the same x-axis. The y-axes for the bar and line graphs are synchronized and overlaid.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): The column name to be used for the x-axis.
        y_column (str): The column name to be used for the y-axis 1, representing the column chart.
        y_line (str): The column name to be used for the y-axis 2, representing the line chart.

    Returns:
        go.Figure: : A Plotly Figure object representing the combined column and line chart.

    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=data_frame[x], y=data_frame[y_column], name=y_column),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=data_frame[x], y=data_frame[y_line], name=y_line),
        secondary_y=True,
    )

    fig.update_layout(
        xaxis={"type": "category", "title": x},
        yaxis={"tickmode": "sync", "title": y_column},
        yaxis2={"tickmode": "sync", "overlaying": "y", "title": y_line},
    )

    return fig


@capture("graph")
def categorical_column(data_frame: pd.DataFrame, x: str, y: str):
    """Creates a column chart where the x-axis values are converted to category type."""
    fig = px.bar(
        data_frame,
        x=x,
        y=y,
    )
    # So ticks are aligned with bars when xaxes values are numbers (e.g. years)
    fig.update_xaxes(type="category")
    return fig


@capture("graph")
def waterfall(data_frame: pd.DataFrame, x: str, y: str, measure: List[str]) -> go.Figure:
    """Creates a waterfall chart using Plotly's `go.Waterfall`.

    A Waterfall chart visually breaks down the cumulative effect of sequential positive and negative values,
    showing how each value contributes to the total.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): Column name in `data_frame` for x-axis values.
        y (str): Column name in `data_frame` for y-axis values.
        measure (List[str]): List specifying the type of each bar, can be "relative", "total", or "absolute".

    Returns:
        go.Figure: A Plotly Figure object representing the Waterfall chart.

    For additional parameters and customization options, see the Plotly documentation:
    https://plotly.com/python/reference/waterfall/

    """
    fig = go.Figure(
        go.Waterfall(
            x=data_frame[x],
            y=data_frame[y],
            measure=data_frame[measure],
        )
    )
    fig.update_layout(showlegend=False)
    return fig


@capture("graph")
def radar(data_frame, **kwargs) -> go.Figure:
    """Creates a radar chart using Plotly's `line_polar`.

    A radar chart is a type of data visualization in which there are three or more
    variables represented on axes that originate from the same central point.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        **kwargs: Keyword arguments that can be passed into Plotly's line_polar (i.e. r, theta, etc.)

    Returns:
        go.Figure: A Plotly Figure object representing the radar chart.

    """
    fig = px.line_polar(data_frame, **kwargs)
    fig.update_traces(fill="toself")
    return fig


@capture("graph")
def dumbbell(data_frame: pd.DataFrame, x: str, y: str, color: str) -> go.Figure:
    """Creates a dumbbell chart using Plotly's `px.scatter` and `add_shape`.

    A dumbbell plot is a type of dot plot where the points, displaying different groups, are connected with a straight
    line. They are ideal for illustrating differences or gaps between two points.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): Column name in `data_frame` for x-axis values.
        y (str): Column name in `data_frame` for y-axis values.
        color (str): Column name in `data_frame` used for coloring the markers.

    Returns:
        go.Figure: A Plotly Figure object representing the dumbbell chart.

    Inspired by: https://community.plotly.com/t/how-to-make-dumbbell-plots-in-plotly-python/47762

    """
    # Add two dots to plot
    fig = px.scatter(data_frame, y=y, x=x, color=color)

    # Add lines between dots
    for y_value, group in data_frame.groupby(y):
        fig.add_shape(
            type="line",
            layer="below",
            y0=y_value,
            y1=y_value,
            x0=group[x].min(),
            x1=group[x].max(),
            line_color="grey",
            line_width=3,
        )

    # Increase size of dots
    fig.update_traces(marker_size=12)
    return fig
