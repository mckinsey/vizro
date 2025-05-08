"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

page_1 = vm.Page(
    title="Page-1",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

page_2 = vm.Page(
    title="Page-2",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Filter(column="sepal_length"),
    ],
)

dashboard = vm.Dashboard(
    pages=[page_1, page_2],
    title="Dash 3.0 smoke test",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
