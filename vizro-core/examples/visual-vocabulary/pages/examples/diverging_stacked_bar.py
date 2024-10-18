import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

pastries = pd.DataFrame(
    {
        "pastry": [
            "Scones",
            "Bagels",
            "Muffins",
            "Cakes",
            "Donuts",
            "Cookies",
            "Croissants",
            "Eclairs",
            "Brownies",
        ],
        "Strongly Disagree": [-20, -30, -10, -5, -15, -5, -10, -25, -8],
        "Disagree": [-30, -25, -20, -10, -20, -10, -15, -30, -12],
        "Agree": [30, 25, 40, 40, 45, 40, 40, 25, 40],
        "Strongly Agree": [20, 20, 30, 45, 20, 45, 35, 20, 40],
    }
)


@capture("graph")
def diverging_stacked_bar(data_frame, **kwargs) -> go.Figure:
    """Creates a horizontal diverging stacked bar chart (with positive and negative values only).

    This type of chart is a variant of the standard stacked bar chart, with bars aligned on a central baseline to
    show both positive and negative values. Each bar is segmented to represent different categories.

    This function is not suitable for diverging stacked bar charts that include a neutral category.

    Inspired by: https://community.plotly.com/t/need-help-in-making-diverging-stacked-bar-charts/34023

    Args:
        data_frame (pd.DataFrame): The data frame for the chart. Can be long form or wide form.
            See https://plotly.com/python/wide-form/.
        **kwargs: Keyword arguments to pass into px.bar (e.g. x, y, labels).

    Returns:
       go.Figure: A Plotly Figure object representing the horizontal diverging stacked bar chart.
    """
    fig = px.bar(data_frame, **kwargs)

    for i, trace in enumerate(fig.data):
        trace.update(legendrank=i)

    if "color_discrete_sequence" not in kwargs and "color_discrete_map" not in kwargs:
        colorscale = [list(x) for x in fig.layout.template.layout.colorscale.diverging]
        colors = px.colors.sample_colorscale(colorscale, len(fig.data), 0.2, 0.8)
        for trace, color in zip(fig.data, colors):
            trace.update(marker_color=color)

    orientation = fig.data[0].orientation
    negative_traces = {
        trace_idx: trace
        for trace_idx, trace in enumerate(fig.data)
        if all(value <= 0 for value in getattr(trace, "x" if orientation == "h" else "y"))
    }
    mutable_traces = list(fig.data)
    for trace_idx, trace in zip(reversed(negative_traces.keys()), negative_traces.values()):
        mutable_traces[trace_idx] = trace
    fig.data = mutable_traces

    if orientation == "h":
        fig.add_vline(x=0, line_width=2, line_color="grey")
    else:
        fig.add_hline(y=0, line_width=2, line_color="grey")

    return fig


page = vm.Page(
    title="Diverging stacked bar",
    components=[
        vm.Graph(
            title="I would recommend this pastry to my friends",
            figure=diverging_stacked_bar(
                data_frame=pastries,
                x=["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"],
                y="pastry",
                labels={"value": "Response count", "variable": "Opinion"},
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
