"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

tips = px.data.tips()


@capture("graph")
def dumbbell(data_frame, x, y, color):
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
    # Add two dots to plot
    fig = px.scatter(data_frame, y=y, x=x, color=color)

    # Add lines between dots
    for i in data_frame[y].unique():
        df_sub = data_frame[data_frame[y] == i]
        fig.add_shape(
            type="line",
            layer="below",
            y0=df_sub[y].values[0],
            x0=df_sub[x].values[0],
            y1=df_sub[y].values[1],
            x1=df_sub[x].values[1],
            line_color="grey",
        )

    # Increase size of dots
    fig.update_traces(marker_size=12)
    return fig


page = vm.Page(
    title="Dumbbell",
    components=[
        vm.Graph(
            figure=dumbbell(
                tips.groupby(["day", "sex"]).agg({"tip": "sum"}).reset_index(), y="day", x="tip", color="sex"
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()

if __name__ == "__main__":
    Vizro().build(dashboard).run()
