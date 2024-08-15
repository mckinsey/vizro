import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()


page = vm.Page(
    title="Paired column",
    components=[
        vm.Graph(
            figure=px.histogram(
                tips,
                x="day",
                y="total_bill",
                color="sex",
                barmode="group",
                category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
            ),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
