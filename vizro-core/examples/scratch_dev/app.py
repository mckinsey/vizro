"""Dev app to try things out."""

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture


@capture("graph")
def lollipop(data_frame: pd.DataFrame, x: str, y: str):
    """Creates a lollipop chart using Plotly.

    This function generates a scatter chart and then draws lines extending from each point to the x-axis.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): The column name to be used for the x-axis.
        y (str): The column name to be used for the y-axis.

    Returns:
        go.Figure: : A Plotly Figure object representing the lollipop chart.
    """
    fig = go.Figure()

    # Draw points
    fig.add_trace(
        go.Scatter(
            x=data_frame[x],
            y=data_frame[y],
            mode="markers",
            marker=dict(color="#00b4ff", size=12),
        )
    )

    for i in range(len(data_frame)):
        fig.add_trace(
            go.Scatter(
                x=[0, data_frame[x].iloc[i]],
                y=[data_frame[y].iloc[i], data_frame[y].iloc[i]],
                mode="lines",
                line=dict(color="#00b4ff", width=3),
            )
        )
    fig.update_layout(showlegend=False)
    return fig


gapminder = px.data.gapminder()


page = vm.Page(
    title="Lollipop",
    components=[
        vm.Graph(figure=lollipop(gapminder.query("year == 2007 and gdpPercap > 36000"), y="country", x="gdpPercap"))
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
