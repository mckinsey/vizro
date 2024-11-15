import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture

gapminder = px.data.gapminder()


@capture("graph")
def lollipop(data_frame: pd.DataFrame, **kwargs):
    """Creates a lollipop chart using Plotly."""
    fig = px.scatter(data_frame, **kwargs)

    # Enable for both orientations
    is_horizontal = fig.data[0].orientation == "h"
    x_coords = [[0, x] if is_horizontal else [x, x] for x in fig.data[0]["x"]]
    y_coords = [[y, y] if is_horizontal else [0, y] for y in fig.data[0]["y"]]
    for x, y in zip(x_coords, y_coords):
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines"))

    xaxis_showgrid = is_horizontal
    yaxis_showgrid = not is_horizontal

    fig.update_traces(
        marker_size=12,
        line_width=3,
        line_color=fig.layout.template.layout.colorway[0],
    )

    fig.update_layout(
        showlegend=False, yaxis_showgrid=yaxis_showgrid, xaxis_showgrid=xaxis_showgrid, yaxis_rangemode="tozero"
    )
    return fig


fig = lollipop(
    data_frame=gapminder.query("year == 2007 and gdpPercap > 36000").sort_values("gdpPercap"),
    y="country",
    x="gdpPercap",
)
