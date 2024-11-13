from typing import Union

import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from plotly.subplots import make_subplots
from vizro.models.types import capture


@capture("graph")
def column_and_line(
    data_frame: pd.DataFrame,
    x: Union[str, pd.Series, list[str], list[pd.Series]],
    y_column: Union[str, pd.Series, list[str], list[pd.Series]],
    y_line: Union[str, pd.Series, list[str], list[pd.Series]],
) -> go.Figure:
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


gapminder = px.data.gapminder().query("country == 'Vietnam'")

fig = column_and_line(gapminder, y_column="gdpPercap", y_line="lifeExp", x="year")
