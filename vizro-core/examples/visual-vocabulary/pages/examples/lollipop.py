import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vizro.models.types import capture

gapminder = px.data.gapminder()

@capture("graph")
def lollipop(data_frame: pd.DataFrame, **kwargs):
    """Creates a lollipop chart using Plotly."""
    fig = px.scatter(data_frame, **kwargs)
    x_array = fig.data[0].x
    y_array = fig.data[0].y

    for i in range(len(data_frame)):
        fig.add_trace(
            go.Scatter(
                x=[0, x_array[i]],
                y=[y_array[i], y_array[i]],
                mode="lines",
            )
        )

    fig.update_traces(marker_size=12, line_width=3, line_color=fig.layout.template.layout.colorway[0])
    fig.update_layout(showlegend=False)
    fig.update_layout(yaxis_title="", yaxis_showgrid=False)
    return fig

fig = lollipop(data_frame=gapminder.query("year == 2007 and gdpPercap > 36000").sort_values("gdpPercap"), y="country", x="gdpPercap")
