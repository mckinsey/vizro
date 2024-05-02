from flask_caching import Cache
from vizro import Vizro
import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm

from vizro.managers import data_manager
from vizro.models.types import CapturedCallable, capture


# Note need to specify default value if have Filter since that calls data load function
# Then have problem that filter options don't get updated when data source changes
@capture("action")
def load_iris_data(points):
    iris = px.data.iris()
    return iris.sample(points)


# Options if have Filter. For advanced users only:
# 1. use CapturedCallable and load_iris(5) --> confusing because then looks like it's actually loading the data.
# Better for reusing same callable across multiple data sources. Harder to compose together.
# 2. use function with default arguments --> then will we ever use CC for it in future? Not to good for reusing same
# callable.
# One advantage of CC that's not relevant is ability to specify from YAML.
# Catch that need to specify same default argument as in parameter value is same with both approachces.

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
data_manager["iris"] = load_iris_data(5)
data_manager["iris"].timeout = 10

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(id="graph", figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Parameter(targets=["graph.x"], selector=vm.RadioItems(options=["sepal_length", "sepal_width"])),
        vm.Parameter(targets=["graph.data_frame.points"], selector=vm.Slider(min=1, max=10, step=1)),
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
