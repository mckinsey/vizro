"""Scratch app."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            figure=px.scatter_matrix(
                df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
# Vizro().build(dashboard).run()

if __name__ == "__main__":
    # Move app definition outside of __main__ block for the HF demo to work
    app = Vizro().build(dashboard)
