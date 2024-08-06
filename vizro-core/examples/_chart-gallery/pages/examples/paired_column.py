import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()
tips_grouped = tips.groupby(["sex", "smoker"]).agg({"total_bill": "sum"}).reset_index()

page = vm.Page(
    title="Paired Column",
    components=[vm.Graph(figure=px.bar(tips_grouped, x="sex", y="total_bill", color="smoker", barmode="group"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
