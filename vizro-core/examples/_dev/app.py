"""Example to show dashboard configuration."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.tables import dash_ag_grid

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Card(text="""hello"""),
        vm.AgGrid(figure=dash_ag_grid(df))
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
