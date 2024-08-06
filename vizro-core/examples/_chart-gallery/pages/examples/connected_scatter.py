import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Connected Scatter",
    components=[
        vm.Graph(
            figure=px.line(
                gapminder.query("continent == 'Oceania'"), x="year", y="lifeExp", color="country", markers=True
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
