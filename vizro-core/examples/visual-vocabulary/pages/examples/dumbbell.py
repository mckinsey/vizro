import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from plotly import graph_objects as go
from vizro import Vizro
from vizro.models.types import capture

tips = px.data.tips()


@capture("graph")
def dumbbell(data_frame: pd.DataFrame, x: str, y: str, color: str) -> go.Figure:
    # Add two dots to plot
    fig = px.scatter(data_frame, y=y, x=x, color=color)

    # Add lines between dots
    for y_value, group in data_frame.groupby(y):
        fig.add_shape(
            type="line",
            layer="below",
            y0=y_value,
            y1=y_value,
            x0=group[x].min(),
            x1=group[x].max(),
            line_color="grey",
            line_width=3
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
