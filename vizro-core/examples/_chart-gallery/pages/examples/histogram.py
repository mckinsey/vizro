import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Histogram",
    components=[vm.Graph(px.histogram(tips, x="total_bill"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
