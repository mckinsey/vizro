import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def lollipop(data_frame: pd.DataFrame, **kwargs):
    """Creates a lollipop chart using Plotly."""
    fig = px.scatter(data_frame, **kwargs)

    orientation = fig.data[0].orientation
    x_or_y = "x" if orientation == "h" else "y"
    y_or_x = "y" if orientation == "h" else "x"

    for x_or_y_value, y_or_x_value in zip(fig.data[0][x_or_y], fig.data[0][y_or_x]):
        fig.add_trace(go.Scatter({x_or_y: [0, x_or_y_value], y_or_x: [y_or_x_value, y_or_x_value], "mode": "lines"}))

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


gapminder = (
    px.data.gapminder()
    .query("year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])")
    .sort_values("pop")
)

fig = lollipop(gapminder, y="country", x="pop")
