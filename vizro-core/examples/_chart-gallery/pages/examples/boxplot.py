import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Boxplot",
    components=[
        vm.Graph(figure=px.boxplot(tips, y="total_bill", x="day", color="day")),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
