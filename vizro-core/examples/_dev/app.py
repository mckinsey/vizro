from vizro import Vizro
import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm

from vizro.managers import data_manager

def load_iris_data():
    iris = px.data.iris()
    return iris.sample(50)

data_manager["iris"] = load_iris_data

page = vm.Page(
    title="Update the chart on page refresh",
    components=[
        vm.Graph(figure=px.box("iris", x="species", y="petal_width", color="species"))
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()