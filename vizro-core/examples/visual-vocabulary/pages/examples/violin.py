import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Violin",
    components=[
        vm.Graph(figure=px.violin(tips, y="total_bill", x="day", color="day", box=True)),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
