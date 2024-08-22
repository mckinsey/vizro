import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Bubble",
    components=[
        vm.Graph(figure=px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", size_max=60))
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
