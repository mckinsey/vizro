import time

import e2e.vizro.constants as cnst
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager


def load_iris_data_sample(number_of_points=10):
    time.sleep(0.25)  # for testing, to catch reloading of the chart
    return px.data.iris().sample(number_of_points)


def load_iris_data_head(number_of_points=150):
    time.sleep(0.25)  # for testing, to catch reloading of the chart
    return px.data.iris().head(number_of_points)


data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})
data_manager["iris_cached"] = load_iris_data_sample
data_manager["iris_cached"].timeout = 300
data_manager["iris_not_cached"] = load_iris_data_sample
data_manager["iris_not_cached"].timeout = -1  # NOT cached
data_manager["iris_head"] = load_iris_data_head
data_manager["iris_head"].timeout = -1  # NOT cached

dynamic_data_page = vm.Page(
    title=cnst.DYNAMIC_DATA_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_DYNAMIC_CACHED_ID,
            figure=px.scatter("iris_cached", x="species", y="petal_width", color="species"),
        ),
        vm.Graph(
            id=cnst.SCATTER_DYNAMIC_ID,
            figure=px.scatter("iris_not_cached", x="species", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.SCATTER_DYNAMIC_CACHED_ID}.data_frame.number_of_points"],
            selector=vm.Slider(id=cnst.SLIDER_DYNAMIC_DATA_CACHED_ID, min=10, max=100, step=10, value=10),
        ),
        vm.Parameter(
            targets=[f"{cnst.SCATTER_DYNAMIC_ID}.data_frame.number_of_points"],
            selector=vm.Slider(id=cnst.SLIDER_DYNAMIC_DATA_ID, min=10, max=100, step=10, value=10),
        ),
    ],
)


dynamic_data_df_parameter_page = vm.Page(
    title=cnst.DYNAMIC_DATA_DF_PARAMETER_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_DF_PARAMETER,
            figure=px.scatter(
                data_frame="iris_head",
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
        vm.Graph(
            id=cnst.SCATTER_DF_STATIC,
            figure=px.scatter(
                data_frame=px.data.iris().tail(50),
                x="sepal_width",
                y="sepal_length",
                color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"},
            ),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.RadioItems(id=cnst.RADIOITEMS_FILTER_DF_PARAMETER)),
        vm.Parameter(
            targets=[f"{cnst.SCATTER_DF_PARAMETER}.data_frame.number_of_points"],
            selector=vm.Slider(
                id=cnst.SLIDER_DF_PARAMETER,
                min=0,
                max=150,
                value=150,
                title="Number of points",
                step=10,
            ),
        ),
    ],
)
