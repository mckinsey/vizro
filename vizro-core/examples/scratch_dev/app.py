"""Test app"""

from vizro import Vizro
import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm

from vizro.managers import data_manager


def load_iris_data():
    iris = px.data.iris()
    return iris.sample(50)


data_manager["iris"] = load_iris_data
gapminder = px.data.gapminder()

page = vm.Page(
    title="Update the chart on page refresh",
    components=[
        vm.Graph(figure=px.box("iris", x="species", y="petal_width", color="species")),
        vm.Graph(figure=px.box(gapminder, x="year", y="lifeExp", color="continent")),
    ],
    controls=[
        vm.Filter(column="continent"),
        vm.Filter(column="species", selector=vm.Checklist()),
        vm.Filter(column="species"),
        vm.Filter(column="petal_width"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
