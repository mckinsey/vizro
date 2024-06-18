"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.gapminder()

page_one = vm.Page(
    title="Vizro filters exporting",
    components=[
        vm.Graph(id="graph_1", figure=px.scatter(df, x="gdpPercap", y="lifeExp", color="continent", size="pop")),
        vm.Graph(id="graph_2", figure=px.scatter(df, x="gdpPercap", y="lifeExp", color="continent", size="pop")),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)

dashboard = vm.Dashboard(pages=[page_one])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
