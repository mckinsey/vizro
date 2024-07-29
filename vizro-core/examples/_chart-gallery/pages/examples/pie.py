import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Pie",
    components=[vm.Graph(figure=px.pie(tips, values="tip", names="day"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
