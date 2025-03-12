"""Dev app to try things out."""

import time
import yaml

import dash
import pandas as pd
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from functools import partial


SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}
BAR_CHART_CONF = dict(x="species", color="species", color_discrete_map=SPECIES_COLORS)
SCATTER_CHART_CONF = dict(x="sepal_length", y="petal_length", color="species", color_discrete_map=SPECIES_COLORS)


def _get_static_iris():
    static_iris = px.data.iris()
    static_iris["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(static_iris), freq="D")
    return static_iris


def load_dynamic_iris_data():
    time.sleep(0.5)

    df = _get_static_iris()

    with open("data.yaml", "r") as file:
        data = {
            "setosa": 0,
            "versicolor": 0,
            "virginica": 0,
            "min": 0,
            "max": 10,
            "date_min": "2024-01-01",
            "date_max": "2024-05-29",
        }
        data.update(yaml.safe_load(file) or {})

    date_min = pd.to_datetime(data["date_min"])
    date_max = pd.to_datetime(data["date_max"])
    df = df[df["date_column"].between(date_min, date_max, inclusive="both")]

    return df


data_manager["static_iris"] = _get_static_iris()
data_manager["dynamic_iris"] = load_dynamic_iris_data


page_1 = vm.Page(
    title="Dynamic vs Static filter",
    components=[
        vm.Graph(
            id="dynamic_graph",
            title="Dynamic Graph",
            figure=px.bar(data_frame="dynamic_iris", **BAR_CHART_CONF),
        ),
        vm.Graph(
            id="static_graph",
            title="Static Graph",
            figure=px.scatter(data_frame="static_iris", **SCATTER_CHART_CONF),
        ),
    ],
    controls=[
        # Dynamic Single
        vm.Filter(
            column="date_column",
            targets=["dynamic_graph"],
            selector=vm.DatePicker(title="Dynamic Single", range=False),
        ),
        # Dynamic Multi
        vm.Filter(
            column="date_column",
            targets=["dynamic_graph"],
            selector=vm.DatePicker(title="Dynamic Multi"),
        ),
        # Static Single
        vm.Filter(
            column="date_column",
            targets=["static_graph"],
            selector=vm.DatePicker(title="Static Single", range=False),
        ),
        # Static Multi
        vm.Filter(
            column="date_column",
            targets=["static_graph"],
            selector=vm.DatePicker(title="Static Multi"),
        ),
        # Default one (targets static and dynamic graphs):
        vm.Filter(column="date_column"),
        # Other filter types:
        # vm.Filter(column="species"),
        # vm.Filter(column="sepal_length"),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
