import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

tips = px.data.tips()

@capture("graph")
def dumbbell(data_frame, x, y, color):
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
    fig.update_traces(marker=dict(size=12))
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
