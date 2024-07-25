import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder_2007 = px.data.gapminder().query("year == 2007")

page = vm.Page(
    title="Choropleth",
    components=[
        vm.Graph(
            figure=px.choropleth(
                gapminder_2007,
                locations="iso_alpha",
                color="lifeExp",
                hover_name="country",
            )
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
