"""Scratch dev app."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

page = vm.Page(
    title="Default Dash AG Grid",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=px.data.gapminder())),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
