import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

wind = px.data.wind()

page = vm.Page(
    title="Radar chart",
    components=[
        vm.Graph(figure=px.line_polar(wind, r="frequency", theta="direction", color="strength", line_close=True))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
