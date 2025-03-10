"""Contains custom charts used inside the dashboard."""

from typing import Union

import pandas as pd
import vizro.plotly.express as px
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from vizro.models.types import capture


# TODO: consider how this should be represented in the code example files. Since the code is copy and pasted
# it can get out of sync. But probably we don't want the docstrings in the short code snippet.
# Ultimately these charts will probably move to vizro.charts anyway.
@capture("graph")
def butterfly(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates a butterfly chart based on px.bar.

    A butterfly chart is a type of bar chart where two sets of bars are displayed back-to-back, often used to compare
    two sets of data.

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.bar (e.g. x, y, labels).
            See https://plotly.com/python-api-reference/generated/plotly.express.bar.html.

    Returns:
        go.Figure: Butterfly chart.

    """
    fig = px.bar(data_frame, **kwargs)

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"

    # Create new x or y axis with scale reversed (so going from 0 at the midpoint outwards) to do back-to-back bars.
    fig.update_traces({f"{x_or_y}axis": f"{x_or_y}2"}, selector=1)
    fig.update_layout({f"{x_or_y}axis2": fig.layout[f"{x_or_y}axis"]})
    fig.update_layout(
        {f"{x_or_y}axis": {"autorange": "reversed", "domain": [0, 0.5]}, f"{x_or_y}axis2": {"domain": [0.5, 1]}}
    )

    if orientation == "h":
        fig.add_vline(x=0, line_width=2, line_color="grey")
    else:
        fig.add_hline(y=0, line_width=2, line_color="grey")

    return fig


@capture("graph")
def sankey(data_frame: pd.DataFrame, source: str, target: str, value: str, labels: list[str]) -> go.Figure:
    """Creates a Sankey chart based on go.Sankey.

    A Sankey chart is a type of flow diagram where the width of the arrows is proportional to the flow rate.
    It is used to visualize the flow of resources or data between different stages or categories.

    For detailed information on additional parameters and customization, refer to the Plotly documentation:
    https://plotly.com/python/reference/sankey/

    Args:
        data_frame: DataFrame for the chart.
        source: The name of the column in data_frame for source nodes.
        target: The name of the column in data_frame for target nodes.
        value: The name of the column in data_frame for the values representing the flow between nodes.
        labels: A list of labels for the nodes.

    Returns:
        go.Figure: Sankey chart.
    """
    return go.Figure(
        data=go.Sankey(
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
        ),
        layout={"barmode": "relative"},
    )


@capture("graph")
def column_and_line(
    data_frame: pd.DataFrame,
    x: Union[str, pd.Series, list[str], list[pd.Series]],
    y_column: Union[str, pd.Series, list[str], list[pd.Series]],
    y_line: Union[str, pd.Series, list[str], list[pd.Series]],
) -> go.Figure:
    """Creates a combined column and line chart based on px.bar and px.line.

    This function generates a chart with a bar graph for one variable (y-axis 1) and a line graph for another variable
    (y-axis 2), sharing the same x-axis. The y-axes for the bar and line graphs are synchronized and overlaid.

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        x: Either a name of a column in data_frame, or a pandas Series or array_like object.
        y_column: Either a name of a column in data_frame, or a pandas Series or array_like object.
        y_line: Either a name of a column in data_frame, or a pandas Series or array_like object.

    Returns:
        go.Figure: Combined column and line chart.

    """
    # We use px.bar and px.line so that we get the plotly express hoverdata, axes titles etc. Bar is used arbitrarily
    # selected as the "base" plot and then line added on top of it. This means manually incrementing
    # color_discrete_sequence for the line plot so that the colors are not the same for bar and line.
    bar = px.bar(data_frame, x=x, y=y_column)
    fig = make_subplots(figure=bar, specs=[[{"secondary_y": True}]])

    line = px.line(
        data_frame,
        x=x,
        y=y_line,
        markers=True,
        color_discrete_sequence=fig.layout.template.layout.colorway[len(bar.data) :],
    )

    for trace in line.data:
        fig.add_trace(trace, secondary_y=True)

    fig.update_layout(yaxis2={"tickmode": "sync", "overlaying": "y", "title": line.layout.yaxis.title})

    return fig


@capture("graph")
def categorical_column(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates categorical bar chart based on px.bar.

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.bar (e.g. x, y, labels).
            See https://plotly.com/python-api-reference/generated/plotly.express.bar.html.

    Returns:
       go.Figure: Categorical column chart.

    """
    fig = px.bar(data_frame, **kwargs)
    # So ticks are aligned with bars when xaxes values are numbers (e.g. years)
    fig.update_xaxes(type="category")
    return fig


@capture("graph")
def waterfall(data_frame: pd.DataFrame, x: str, y: str, measure: list[str]) -> go.Figure:
    """Creates a waterfall chart based on go.Waterfall.

    A Waterfall chart visually breaks down the cumulative effect of sequential positive and negative values,
    showing how each value contributes to the total.

    For additional parameters and customization options, see the Plotly documentation:
    https://plotly.com/python/reference/waterfall/

    Args:
        data_frame: TDataFrame for the chart.
        x: Column name in data_frame for x-axis values.
        y: Column name in data_frame for y-axis values.
        measure: List specifying the type of each bar, can be "relative", "total", or "absolute".

    Returns:
        go.Figure: Waterfall chart.
    """
    return go.Figure(
        data=go.Waterfall(x=data_frame[x], y=data_frame[y], measure=data_frame[measure]),
        layout={"showlegend": False},
    )


@capture("graph")
def radar(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates a radar chart based on px.line_polar.

    A radar chart is a type of data visualization in which there are three or more
    variables represented on axes that originate from the same central point.

    Args:
        data_frame: DataFrame for the chart.
        **kwargs: Keyword arguments to pass into px.line_polar (e.g. r, theta).
            See https://plotly.com/python-api-reference/generated/plotly.express.line_polar.html.

    Returns:
       go.Figure: A Plotly Figure object of the radar chart.

    """
    fig = px.line_polar(data_frame, **kwargs)
    fig.update_traces(fill="toself")
    return fig


@capture("graph")
def dumbbell(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates a dumbbell chart based on px.scatter.

    A dumbbell plot is a type of dot plot where the points, displaying different groups, are connected with a straight
    line. They are ideal for illustrating differences or gaps between two points.

    Inspired by: https://community.plotly.com/t/how-to-make-dumbbell-plots-in-plotly-python/47762

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.scatter (e.g. x, y, labels).
            See https://plotly.com/python-api-reference/generated/plotly.scatter.html.

    Returns:
        go.Figure: Dumbbell chart.
    """
    fig = px.scatter(data_frame, **kwargs)

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"
    y_or_x = "y" if orientation == "h" else "x"

    # Add lines between every pair of points.
    for x_or_y_0, x_or_y_1, y_or_x_0, y_or_x_1 in zip(
        fig.data[0][x_or_y],
        fig.data[1][x_or_y],
        fig.data[0][y_or_x],
        fig.data[1][y_or_x],
    ):
        fig.add_shape(
            **{f"{x_or_y}0": x_or_y_0, f"{x_or_y}1": x_or_y_1, f"{y_or_x}0": y_or_x_0, f"{y_or_x}1": y_or_x_1},
            type="line",
            layer="below",
            line_color="grey",
            line_width=3,
        )

    fig.update_traces(marker_size=12)
    return fig


@capture("graph")
def diverging_stacked_bar(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    """Creates a diverging stacked bar chart based on px.bar.

    This type of chart is a variant of the standard stacked bar chart, with bars aligned on a central baseline to
    show both positive and negative values. Each bar is segmented to represent different categories.

    This function is not suitable for diverging stacked bar charts that include a neutral category. The first half of
    bars plotted are assumed to be negative ("Disagree") and the second half are assumed to be positive ("Agree").

    Inspired by: https://community.plotly.com/t/need-help-in-making-diverging-stacked-bar-charts/34023

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.bar (e.g. x, y, labels).
            See https://plotly.com/python-api-reference/generated/plotly.express.bar.html.

    Returns:
       go.Figure: Diverging stacked bar chart.
    """
    fig = px.bar(data_frame, **kwargs)

    # Fix legend position according to the order of traces. This ensures that "Strongly disagree" comes before
    # "Disagree".
    for i, trace in enumerate(fig.data):
        trace.update(legendrank=i)

    if "color_discrete_sequence" not in kwargs and "color_discrete_map" not in kwargs:
        # Make a discrete diverging colorscale by sampling the right number of colors.
        # Need to explicitly convert colorscale to list of lists due to plotly bug/inconsistency:
        # https://github.com/plotly/plotly.py/issues/4808
        colorscale = [list(x) for x in fig.layout.template.layout.colorscale.diverging]
        colors = px.colors.sample_colorscale(colorscale, len(fig.data), 0.2, 0.8)
        for trace, color in zip(fig.data, colors):
            trace.update(marker_color=color)

    # Plotly draws traces in order they appear in fig.data, starting from x=0 and then stacking outwards.
    # We need negative traces to be ordered so that "Disagree" comes before "Strongly disagree", so reverse the
    # order of first half of traces.
    mutable_traces = list(fig.data)
    mutable_traces[: len(fig.data) // 2] = reversed(fig.data[: len(fig.data) // 2])
    fig.data = mutable_traces

    # Create new x or y axis with scale reversed (so going from 0 at the midpoint outwards) to do negative bars.
    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"

    for trace_idx in range(len(fig.data) // 2, len(fig.data)):
        fig.update_traces({f"{x_or_y}axis": f"{x_or_y}2"}, selector=trace_idx)

    # Add ticksuffix and range limitations on both sids for correct interpretation of diverging stacked bar
    # with percentage data
    fig.update_layout({f"{x_or_y}axis": {"ticksuffix": "%"}})
    fig.update_layout({f"{x_or_y}axis2": fig.layout[f"{x_or_y}axis"]})
    fig.update_layout(
        {
            f"{x_or_y}axis": {"domain": [0, 0.5], "range": [100, 0]},
            f"{x_or_y}axis2": {"domain": [0.5, 1], "range": [0, 100]},
        }
    )

    if orientation == "h":
        fig.add_vline(x=0, line_width=2, line_color="grey")
    else:
        fig.add_hline(y=0, line_width=2, line_color="grey")

    return fig


@capture("graph")
def lollipop(data_frame: pd.DataFrame, **kwargs):
    """Creates a lollipop based on px.scatter.

    A lollipop chart is a variation of a bar chart where each data point is represented by a line and a dot at the end
    to mark the value.

    Inspired by: https://towardsdatascience.com/lollipop-dumbbell-charts-with-plotly-696039d5f85

    Args:
        data_frame: DataFrame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.scatter (e.g. x, y, labels).
            See https://plotly.com/python-api-reference/generated/plotly.scatter.html.

    Returns:
        go.Figure: Lollipop chart.
    """
    # Plots the dots of the lollipop chart
    fig = px.scatter(data_frame, **kwargs)

    # Enables the orientation of the chart to be either horizontal or vertical
    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"
    y_or_x = "y" if orientation == "h" else "x"

    # Plots the lines of the lollipop chart
    for x_or_y_value, y_or_x_value in zip(fig.data[0][x_or_y], fig.data[0][y_or_x]):
        fig.add_trace(go.Scatter({x_or_y: [0, x_or_y_value], y_or_x: [y_or_x_value, y_or_x_value], "mode": "lines"}))

    # Styles the lollipop chart and makes it uni-colored
    fig.update_traces(
        marker_size=12,
        line_width=3,
        line_color=fig.layout.template.layout.colorway[0],
    )

    fig.update_layout(
        {
            "showlegend": False,
            f"{x_or_y}axis_showgrid": True,
            f"{y_or_x}axis_showgrid": False,
            f"{x_or_y}axis_rangemode": "tozero",
        },
    )
    return fig
