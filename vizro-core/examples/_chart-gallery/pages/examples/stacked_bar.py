import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()
tips_grouped = tips.groupby(["sex", "smoker"]).agg({"total_bill": "sum"}).reset_index()

page = vm.Page(
    title="Stacked Bar",
    components=[vm.Graph(figure=px.bar(tips_grouped, y="sex", x="total_bill", color="smoker", orientation="h"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
