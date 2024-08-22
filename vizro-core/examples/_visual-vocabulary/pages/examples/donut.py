import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Donut",
    components=[vm.Graph(figure=px.pie(tips, values="tip", names="day", hole=0.4))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
