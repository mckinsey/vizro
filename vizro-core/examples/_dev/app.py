"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data
from vizro import Vizro

df = px.data.gapminder()

vm.Page.add_type("controls", vm.Button)

page = vm.Page(
    title="Export from control panel",
    components=[
        vm.Graph(
            id="scatter_graph",
            figure=px.scatter(data_frame=df, x="gdpPercap", y="lifeExp", color="continent")
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
        vm.Button(
            text="Export",
            actions=[vm.Action(function=export_data())]
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
