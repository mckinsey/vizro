import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

wind = px.data.wind()


@capture("graph")
def radar(data_frame, **kwargs):
    """
    Add docstrings here (see butterfly example)
    
    """
    fig = px.line_polar(data_frame, **kwargs)
    fig.update_traces(fill="toself")
    return fig


page = vm.Page(
    title="Radar chart",
    components=[
        vm.Graph(
            figure=radar_chart(
                wind.query("strength =='1-2'"), r="frequency", theta="direction", color="strength", line_close=True
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
