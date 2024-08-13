import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page = vm.Page(
    title="Column",
    components=[
        vm.Graph(
            figure=px.histogram(tips, y="total_bill", x="day", category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]})
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
