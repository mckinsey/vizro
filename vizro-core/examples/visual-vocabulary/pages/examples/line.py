import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

stocks = px.data.stocks()

page = vm.Page(
    title="Line",
    components=[vm.Graph(figure=px.line(stocks, x="date", y="GOOG"))],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
