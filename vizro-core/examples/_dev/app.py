"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from flask_caching import Cache
from vizro import Vizro
from vizro.actions import export_data
from vizro.managers import data_manager


# Note need to specify default value if have Filter since that calls data load function
# Then have problem that filter options don't get updated when data source changes
def load_iris_data(points=1, additional_points=1):
    """Load iris data."""
    iris = px.data.iris()
    return iris.sample(points + additional_points)


data_manager["iris"] = load_iris_data

# If you want to cache the data on the page_2 differently from page_1, you can define another data_manager entry with
# the same function and assign it to the page_2 graphs. e.g. `data_manager["iris_2"] = load_iris_data`

# SimpleCache
data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

# RedisCache
# data_manager.cache = Cache(
#     config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379}
# )

# Timeout
data_manager["iris"].timeout = 30


# TEST CASE:
# There are 2 Parameters per page that control the number of points and additional points.
# Set all of them to same number and see that the output for all of them will be the same if cache is configured,
# otherwise the output will be different.

page_1 = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            id="graph_1", figure=px.scatter(data_frame="iris", x="sepal_length", y="petal_width", color="species")
        ),
        vm.Graph(
            id="graph_2", figure=px.scatter(data_frame="iris", x="sepal_length", y="petal_width", color="species")
        ),
        vm.Button(text="Export", actions=[vm.Action(function=export_data())]),
    ],
    controls=[
        vm.Parameter(
            targets=["graph_1.x", "graph_2.x"], selector=vm.RadioItems(options=["sepal_length", "sepal_width"])
        ),
        vm.Parameter(
            targets=["graph_1.data_frame.points", "graph_1.data_frame.additional_points"],
            selector=vm.Slider(title="Graph 1 points / Graph 1 additional_points", min=1, max=10, step=1),
        ),
        vm.Parameter(
            targets=["graph_2.data_frame.points", "graph_2.data_frame.additional_points"],
            selector=vm.Slider(title="Graph 2 points / Graph 2 additional_points", min=1, max=10, step=1),
        ),
        vm.Filter(column="species", selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"])),
    ],
)

page_2 = vm.Page(
    title="My second page",
    components=[
        vm.Graph(
            id="graph_second_1",
            figure=px.scatter(data_frame="iris", x="sepal_length", y="petal_width", color="species"),
        ),
        vm.Graph(
            id="graph_second_2",
            figure=px.scatter(data_frame="iris", x="sepal_length", y="petal_width", color="species"),
        ),
        vm.Button(text="Export", actions=[vm.Action(function=export_data())]),
    ],
    controls=[
        vm.Parameter(
            targets=["graph_second_1.x", "graph_second_2.x"],
            selector=vm.RadioItems(options=["sepal_length", "sepal_width"]),
        ),
        vm.Parameter(
            targets=["graph_second_1.data_frame.points", "graph_second_2.data_frame.points"],
            selector=vm.Slider(title="Graph 1 points / Graph 2 points", min=1, max=10, step=1),
        ),
        vm.Parameter(
            targets=["graph_second_1.data_frame.additional_points", "graph_second_2.data_frame.additional_points"],
            selector=vm.Slider(title="Graph 1 additional_points / Graph 2 additional_points", min=1, max=10, step=1),
        ),
        vm.Filter(column="species", selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"])),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
