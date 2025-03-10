import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def diverging_stacked_bar(data_frame: pd.DataFrame, **kwargs) -> go.Figure:
    fig = px.bar(data_frame, **kwargs)

    for i, trace in enumerate(fig.data):
        trace.update(legendrank=i)

    if "color_discrete_sequence" not in kwargs and "color_discrete_map" not in kwargs:
        colorscale = [list(x) for x in fig.layout.template.layout.colorscale.diverging]
        colors = px.colors.sample_colorscale(colorscale, len(fig.data), 0.2, 0.8)
        for trace, color in zip(fig.data, colors):
            trace.update(marker_color=color)

    mutable_traces = list(fig.data)
    mutable_traces[: len(fig.data) // 2] = reversed(fig.data[: len(fig.data) // 2])
    fig.data = mutable_traces

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"

    for trace_idx in range(len(fig.data) // 2, len(fig.data)):
        fig.update_traces({f"{x_or_y}axis": f"{x_or_y}2"}, selector=trace_idx)

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
        ],
        "Strongly Disagree": [20, 30, 10, 5, 15, 5, 10, 25],
        "Disagree": [30, 25, 20, 10, 20, 10, 15, 30],
        "Agree": [30, 25, 40, 40, 45, 40, 40, 25],
        "Strongly Agree": [20, 20, 30, 45, 20, 45, 35, 20],
    }
)

fig = diverging_stacked_bar(
    data_frame=pastries,
    x=["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"],
    y="pastry",
    labels={"value": "", "variable": "", "pastry": ""},
    title="I would recommend this pastry to my friends",
)
