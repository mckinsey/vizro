from typing import Union

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from plotly.subplots import make_subplots
from vizro import Vizro
from vizro.models.types import capture

gapminder = px.data.gapminder()


@capture("graph")
def column_and_line(
    data_frame: pd.DataFrame,
    x: Union[str, pd.Series, list[str], list[pd.Series]],
    y_column: Union[str, pd.Series, list[str], list[pd.Series]],
    y_line: Union[str, pd.Series, list[str], list[pd.Series]],
) -> go.Figure:
    """Creates a combined column and line chart using Plotly.

    This function generates a chart with a bar graph for one variable (y-axis 1) and a line graph for another variable
    (y-axis 2), sharing the same x-axis. The y-axes for the bar and line graphs are synchronized and overlaid.

    Args:
        data_frame (pd.DataFrame): The data source for the chart.
        x (str): Either a name of a column in data_frame, or a pandas Series or array_like object.
        y_column (str): Either a name of a column in data_frame, or a pandas Series or array_like object.
        y_line (str): Either a name of a column in data_frame, or a pandas Series or array_like object.

    Returns:
        go.Figure: : A Plotly Figure object of the combined column and line chart.

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


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Column and line",
            components=[
                vm.Graph(
                    figure=column_and_line(
                        gapminder.query("country == 'Vietnam'"),
                        y_column="gdpPercap",
                        y_line="lifeExp",
                        x="year",
                    )
                )
            ],
        )
    ]
)
Vizro().build(dashboard).run()
