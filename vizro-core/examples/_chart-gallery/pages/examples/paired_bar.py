import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()
tips_paired = tips.groupby(["sex", "smoker"]).agg({"total_bill": "sum"}).reset_index()

page = vm.Page(
    title="Paired Bar",
    components=[
        vm.Graph(figure=px.bar(tips_paired, y="sex", x="total_bill", color="smoker", barmode="group", orientation="h"))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
