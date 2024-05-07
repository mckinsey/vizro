"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


def load_iris_data():
    """Load a sample of the iris dataset."""
    iris = px.data.iris()
    return iris.sample(50)


data_manager["iris"] = load_iris_data

page = vm.Page(
    title="Update the chart on page refresh",
    components=[
        vm.Graph(figure=px.violin("iris", x="species", y="petal_width", color="species")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
