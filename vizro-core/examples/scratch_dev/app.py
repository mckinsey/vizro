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

print("INITIALIZING")

SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}
BAR_CHART_CONF = dict(x="species", color="species", color_discrete_map=SPECIES_COLORS)
SCATTER_CHART_CONF = dict(x="sepal_length", y="petal_length", color="species", color_discrete_map=SPECIES_COLORS)


def load_from_file(filter_column=None, parametrized_species=None):
    # Load the full iris dataset
    df = px.data.iris()
    df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")

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

    if filter_column == "species":
        df = pd.concat(
            objs=[
                df[df[filter_column] == "setosa"].head(data["setosa"]),
                df[df[filter_column] == "versicolor"].head(data["versicolor"]),
                df[df[filter_column] == "virginica"].head(data["virginica"]),
            ],
            ignore_index=True,
        )
    elif filter_column == "sepal_length":
        df = df[df[filter_column].between(data["min"], data["max"], inclusive="both")]
    elif filter_column == "date_column":
        date_min = pd.to_datetime(data["date_min"])
        date_max = pd.to_datetime(data["date_max"])
        df = df[df[filter_column].between(date_min, date_max, inclusive="both")]
    else:
        raise ValueError("Invalid filter_column")

    if parametrized_species:
        df = df[df["species"].isin(parametrized_species)]

    return df


data_manager["load_from_file_species"] = partial(load_from_file, filter_column="species")
data_manager["load_from_file_sepal_length"] = partial(load_from_file, filter_column="sepal_length")
data_manager["load_from_file_date_column"] = partial(load_from_file, filter_column="date_column")
df = load_from_file(filter_column="date_column", parametrized_species=["setosa"])
print(df.head())

# TODO-DEV: Turn on/off caching to see how it affects the app.
# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 10})

page_1 = vm.Page(
    title="Dynamic vs Static filter",
    components=[
        vm.Graph(
            id="p1-G-1",
            figure=px.bar(data_frame="load_from_file_date_column", **BAR_CHART_CONF),
        ),
        vm.Graph(
            id="p1-G-2",
            figure=px.scatter(data_frame=px.data.iris(), **SCATTER_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            id="p1-F-1", column="date_column", targets=["p1-G-1"], selector=vm.DatePicker(title="Dynamic filter")
        ),
        vm.Parameter(
            targets=["p1-G-1.x", "p1-G-2.x"],
            selector=vm.RadioItems(options=["species", "sepal_width"], title="Simple X-axis parameter"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    app = Vizro().build(dashboard)

    print("RUNNING\n")

    app.run(dev_tools_hot_reload=False)
