import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()


page = vm.Page(
    title="Bar",
    components=[vm.Graph(figure=px.histogram(tips, x="total_bill", y="day", orientation="h"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
