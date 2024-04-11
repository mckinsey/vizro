"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


def load_iris_data(n):
    """Blah blah blah."""
    iris = px.data.iris()
    return iris.sample(n)  # (2)!


data_manager["iris"] = lambda: load_iris_data(n=10)  # (3)!
data_manager["iris2"] = lambda: load_iris_data(n=30)  # (3)!

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),  # (1)!
        vm.Graph(figure=px.scatter("iris2", x="sepal_length", y="petal_width", color="species")),  # (1)!
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
