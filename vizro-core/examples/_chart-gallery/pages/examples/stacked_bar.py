import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()


page = vm.Page(
    title="Stacked Bar",
    components=[vm.Graph(figure=px.histogram(tips, y="sex", x="total_bill", color="smoker", orientation="h"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
