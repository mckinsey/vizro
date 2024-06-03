"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

page = vm.Page(
    title="Example of a Dash AG Grid",
    components=[
        vm.AgGrid(title="Dash AG Grid", figure=dash_ag_grid(data_frame=df)),
    ],
)
dashboard = vm.Dashboard(pages=[page])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
