import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture


def offset_signal(signal: float, marker_offset: float):
    """Offsets a signal value by marker_offset.

    Reduces for positive signal values and increasing for negative values. Used to reduce the length of
    lines on lollipop charts to end just before the dot.

    Args:
        signal (float): the value to be updated.
        marker_offset (float): the offset to be added/subtracted.

    Returns:
        float: the updated value.

    """
    if abs(signal) <= marker_offset:
        return 0
    return signal - marker_offset if signal > 0 else signal + marker_offset


@capture("graph")
def lollipop(data_frame: pd.DataFrame, x: str, y: str, y_offset: float):
    """Creates a lollipop chart using Plotly.

    This function generates a scatter chart and then draws lines extending from each point to the x-axis.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): The column name to be used for the x-axis.
        y (str): The column name to be used for the y-axis.
        y_offset (float): The amount to offset the end of each line from each scatter point.

    Returns:
        go.Figure: : A Plotly Figure object representing the lollipop chart.

    """
    data = px.scatter(data_frame, x=x, y=y)

    shapes = []
    for i, row in data_frame.iterrows():
        shapes.append(
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": row[x],
                "y0": 0,
                "x1": row[x],
                "y1": offset_signal(row[y], y_offset),
                "line": {"color": "grey", "width": 2},
            }
        )
    fig = data.update_layout(shapes=shapes)
    return fig


gapminder = px.data.gapminder()
df = gapminder.query("year == 2007 and gdpPercap > 36000")
marker_offset = 5.0

page = vm.Page(
    title="Lollipop",
    components=[vm.Graph(figure=lollipop(df, "country", "gdpPercap", marker_offset))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
