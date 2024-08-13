import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()


page = vm.Page(
    title="Stacked Column",
    components=[vm.Graph(figure=px.histogram(tips, x="sex", y="total_bill", color="smoker"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
