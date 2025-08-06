"""Scratch development app."""

import vizro.models as vm
from vizro import Vizro
from vizro.actions import export_data
from vizro.tables import dash_ag_grid
import vizro.plotly.express as px

df_gapminder = px.data.gapminder().query("year == 2007")


page = vm.Page(
    title="My first dashboard",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(figure=dash_ag_grid(df_gapminder)),
        vm.Button(actions=export_data()),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
