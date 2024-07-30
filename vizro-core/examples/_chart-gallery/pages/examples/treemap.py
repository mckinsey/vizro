import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder = px.data.gapminder()
gapminder_2007 = gapminder.query("year == 2007")

page = vm.Page(
    title="Treemap",
    components=[
        vm.Graph(
            figure=px.treemap(
                gapminder_2007, path=[px.Constant("world"), "continent", "country"], values="pop", color="lifeExp"
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
