import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()

page = vm.Page(
    title="Treemap",
    components=[
        vm.Graph(
            figure=px.treemap(
                gapminder.query("year == 2007"),
                path=[px.Constant("world"), "continent", "country"],
                values="pop",
                color="lifeExp",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
