import time

import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


static_df = pd.DataFrame(
    {
        "species": ["artificial_species", "artificial_species", "artificial_species"],
        "sepal_width": [4, 5, 6],
        "sepal_length": [4, 5, 6],
    }
)


def load_data(number_of_points=150):
    # Artificial delay to simulate data loading in production
    print("\nLoading data...\n")
    time.sleep(1)

    return px.data.iris().head(number_of_points)


data_manager["dynamic_df"] = load_data

page_1 = vm.Page(
    title="Update dynamic filter from DFP",
    components=[
        vm.Graph(
            id="dynamic_graph_1",
            figure=px.scatter(data_frame="dynamic_df", x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.Graph(
            figure=px.scatter(data_frame=static_df, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.RadioItems()),
        vm.Parameter(
            targets=["dynamic_graph_1.data_frame.number_of_points"],
            selector=vm.Slider(
                min=0,
                max=150,
                value=150,
                title="Number of points",
                step=10,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
