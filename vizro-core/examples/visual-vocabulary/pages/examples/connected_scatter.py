import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Connected scatter",
    components=[
        vm.Graph(figure=px.line(gapminder.query("country == 'Australia'"), x="year", y="lifeExp", markers=True))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
