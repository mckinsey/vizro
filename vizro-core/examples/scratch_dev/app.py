"""Scratch dev app."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid


df = px.data.iris()

page = vm.Page(
    title="Page",
    layout=vm.Flex(),
    components=[
        vm.Card(text="""BLABLA"""),
        vm.Container(
            variant="outlined", title="Container with AgGrid", components=[vm.AgGrid(figure=dash_ag_grid(df))]
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=False)
