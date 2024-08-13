import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()


page = vm.Page(
    title="Paired bar",
    components=[
        vm.Graph(figure=px.histogram(tips.query("sex=='Female'"), y="sex", x="total_bill", color="smoker", barmode="group", orientation="h"))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
