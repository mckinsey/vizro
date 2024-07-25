import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()
tips_agg = tips.groupby("day").agg({"total_bill": "sum"}).sort_values("total_bill").reset_index()

page = vm.Page(
    title="Bar",
    components=[vm.Graph(figure=px.bar(tips_agg, x="total_bill", y="day", orientation="h"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
