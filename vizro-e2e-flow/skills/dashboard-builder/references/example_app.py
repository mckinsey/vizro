# @LLM: modify these for anything additional you may have added, often not needed
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "vizro",
# ]
# ///

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

#### DATA SETUP #### (@LLM: you need to change this to the usecase!!)
# data_manager["<good_name>"] = pd.read_csv("path/to/your/data.csv") e.g., load your data here
# For demonstration, we load the iris dataset from plotly.express, this allows the example.json to run out-of-the-box
data_manager["iris"] = px.data.iris()


#### CUSTOM CHART SETUP ####
# If you have created any custom chart functions, you can register them here


#### DASHBOARD SETUP ####

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(
            figure=px.scatter(
                "iris", x="sepal_length", y="petal_width", color="species"
            )
        ),
        vm.Graph(
            id="histogram",
            figure=px.histogram(
                "iris", x="sepal_width", color="species", marginal="box"
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species"),
        vm.Parameter(
            targets=["histogram.marginal"],
            selector=vm.RadioItems(
                options=[
                    {"label": "Box", "value": "box"},
                    {"label": "Violin", "value": "violin"},
                    {"label": "Rug", "value": "rug"},
                ],
                value="box",
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])


app = Vizro().build(dashboard)

if __name__ == "__main__":
    app.run(port=8050, debug=True)  # you can change the port if needed
