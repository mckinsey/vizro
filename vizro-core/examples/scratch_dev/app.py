"""This is a test app to test the dashboard layout."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html

df = px.data.iris()


page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
    ],
)


dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
