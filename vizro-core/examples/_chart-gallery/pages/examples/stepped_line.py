import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Stepped line",
    components=[
        vm.Graph(
            figure=px.line(
                data_frame=gapminder.query("country=='China'"),
                x="year",
                y="lifeExp",
                line_shape="hv",
            ),
        )
    ],
)
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
