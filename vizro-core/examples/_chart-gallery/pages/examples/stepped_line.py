import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

stocks = px.data.stocks()

page = vm.Page(
    title="Stepped line",
    components=[
        vm.Graph(
            figure=px.line(
                data_frame=stocks,
                x="date",
                y="GOOG",
                line_shape="hv",
            ),
        )
    ],
)
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
