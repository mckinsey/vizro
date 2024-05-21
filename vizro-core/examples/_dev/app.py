import vizro.models as vm
import vizro.plotly.express as px
from flask_caching import Cache
from vizro import Vizro
from vizro.actions import export_data
from vizro.managers import data_manager


# Note need to specify default value if have Filter since that calls data load function
# Then have problem that filter options don't get updated when data source changes
def load_iris_data(points=1):
    iris = px.data.iris()
    return iris.sample(points)


# TODO: double check cache works correctly.
data_manager["iris"] = load_iris_data

# SimpleCache
# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

# RedisCache
data_manager.cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379})

# Timeout
data_manager["iris"].timeout = 30


page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(id="graph", figure=px.scatter(data_frame="iris", x="sepal_length", y="petal_width", color="species")),
        vm.Button(text="Export", actions=[vm.Action(function=export_data())]),
    ],
    controls=[
        vm.Parameter(targets=["graph.x"], selector=vm.RadioItems(options=["sepal_length", "sepal_width"])),
        vm.Parameter(targets=["graph.data_frame.points"], selector=vm.Slider(min=1, max=10, step=1)),
        vm.Filter(column="species", selector=vm.Dropdown(options=["setosa", "versicolor", "virginica"])),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
