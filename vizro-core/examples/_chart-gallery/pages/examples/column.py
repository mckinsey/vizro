import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()
tips_agg = tips.groupby("day").agg({"total_bill": "sum"}).reset_index()

page = vm.Page(
    title="Column",
    components=[
        vm.Graph(
            figure=px.bar(tips_agg, y="total_bill", x="day", category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]})
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
