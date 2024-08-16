import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Choropleth",
    components=[
        vm.Graph(
            figure=px.choropleth(
                gapminder.query("year == 2007"), locations="iso_alpha", color="lifeExp", hover_name="country"
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
