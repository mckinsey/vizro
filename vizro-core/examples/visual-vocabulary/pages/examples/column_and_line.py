import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from plotly.subplots import make_subplots
from vizro import Vizro
from vizro.models.types import capture

gapminder = px.data.gapminder()


@capture("graph")
def column_and_line(data_frame: pd.DataFrame, x: str, y_column: str, y_line: str) -> go.Figure:
    """Creates a combined column and line chart using Plotly."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=data_frame[x], y=data_frame[y_column], name=y_column),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=data_frame[x], y=data_frame[y_line], name=y_line),
        secondary_y=True,
    )

    fig.update_layout(
        xaxis={"type": "category", "title": x},
        yaxis={"tickmode": "sync", "title": y_column},
        yaxis2={"tickmode": "sync", "overlaying": "y", "title": y_line},
    )

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
