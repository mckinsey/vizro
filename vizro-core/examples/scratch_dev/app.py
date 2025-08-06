# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data

df_gapminder = px.data.gapminder().query("year == 2007")


page = vm.Page(
    title="My first dashboard",
    layout=vm.Flex(),
    components=[
        vm.Graph(figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
        vm.Button(actions=export_data()),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
