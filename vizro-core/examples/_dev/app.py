from vizro import Vizro
import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm

from vizro.managers import data_manager


def load_iris_data():
    iris = pd.read_csv("iris.csv")  # (1)!
    return iris.sample(30)  # (2)!


data_manager["iris"] = load_iris_data  # (3)!

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),  # (1)!
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
