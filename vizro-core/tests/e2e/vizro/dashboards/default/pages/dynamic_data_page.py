import e2e.vizro.constants as cnst
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager


def load_iris_data_sample(number_of_cached_points=10):
    iris = px.data.iris()
    return iris.sample(number_of_cached_points)


def load_iris_data_head(number_of_points=10):
    iris = px.data.iris()
    return iris.head(number_of_points)


data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})
data_manager["iris_sample"] = load_iris_data_sample
data_manager["iris_sample"].timeout = 300
data_manager["iris_head"] = load_iris_data_head
data_manager["iris_head"].timeout = -1  # NOT cached

dynamic_data_page = vm.Page(
    title=cnst.DYNAMIC_DATA_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_DYNAMIC_CACHED_ID,
            figure=px.scatter("iris_sample", x="species", y="petal_width", color="species"),
        ),
        vm.Graph(
            id=cnst.SCATTER_DYNAMIC_ID,
            figure=px.scatter("iris_head", x="species", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.SCATTER_DYNAMIC_CACHED_ID}.data_frame.number_of_cached_points"],
            selector=vm.Slider(id=cnst.SLIDER_DYNAMIC_DATA_CACHED_ID, min=10, max=100, step=10, value=10),
        ),
        vm.Parameter(
            targets=[f"{cnst.SCATTER_DYNAMIC_ID}.data_frame.number_of_points"],
            selector=vm.Slider(id=cnst.SLIDER_DYNAMIC_DATA_ID, min=10, max=100, step=10, value=10),
        ),
    ],
)
