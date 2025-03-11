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


iris = px.data.iris()

page_1 = vm.Page(
    title="Dynamic vs Static filter",
    components=[
        vm.Markdown(
            text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit,
         sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""
        ),
        vm.Graph(
            id="dynamic_graph",
            title="Dynamic Graph",
            figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
        ),
        vm.Graph(
            id="static_graph",
            title="Static Graph",
            figure=px.bar(iris, x="species", y="sepal_length"),
        ),
    ],
    layout=vm.Layout(
        grid=[
            [0, 0],
            *[[1, 2]] * 6,
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
