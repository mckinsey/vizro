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

# Relevant for the "page_6" only
FILTER_COLUMN = "species"
# FILTER_COLUMN = "sepal_length"
# FILTER_COLUMN = "date_column"


def load_from_file(filter_column=FILTER_COLUMN, parametrized_species=None):
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
        raise ValueError("Invalid FILTER_COLUMN")

    if parametrized_species:
        df = df[df["species"].isin(parametrized_species)]

    return df


data_manager["load_from_file"] = load_from_file
data_manager["load_from_file_species"] = partial(load_from_file, filter_column="species")
data_manager["load_from_file_sepal_length"] = partial(load_from_file, filter_column="sepal_length")
data_manager["load_from_file_date_column"] = partial(load_from_file, filter_column="date_column")


# TODO-DEV: Turn on/off caching to see how it affects the app.
# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 10})


homepage = vm.Page(
    title="Homepage",
    components=[
        vm.Card(text="This is the homepage."),
    ],
)

page_1 = vm.Page(
    title="Dynamic vs Static filter",
    components=[
        vm.Graph(
            id="p1-G-1",
            figure=px.bar(data_frame="load_from_file_species", **BAR_CHART_CONF),
        ),
        vm.Graph(
            id="p1-G-2",
            figure=px.scatter(data_frame=px.data.iris(), **SCATTER_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(id="p1-F-1", column="species", targets=["p1-G-1"], selector=vm.Dropdown(title="Dynamic filter")),
        vm.Filter(id="p1-F-2", column="species", targets=["p1-G-2"], selector=vm.Dropdown(title="Static filter")),
        vm.Parameter(
            targets=["p1-G-1.x", "p1-G-2.x"],
            selector=vm.RadioItems(options=["species", "sepal_width"], title="Simple X-axis parameter"),
        ),
    ],
)


page_2 = vm.Page(
    title="Categorical dynamic selectors",
    components=[
        vm.Graph(
            id="p2-G-1",
            figure=px.bar(data_frame="load_from_file_species", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(id="p2-F-1", column="species", selector=vm.Dropdown()),
        vm.Filter(id="p2-F-2", column="species", selector=vm.Dropdown(multi=False)),
        vm.Filter(id="p2-F-3", column="species", selector=vm.Checklist()),
        vm.Filter(id="p2-F-4", column="species", selector=vm.RadioItems()),
        vm.Parameter(
            targets=["p2-G-1.x"],
            selector=vm.RadioItems(
                options=["species", "sepal_width"], value="species", title="Simple X-axis parameter"
            ),
        ),
    ],
)


page_3 = vm.Page(
    title="Numerical dynamic selectors",
    components=[
        vm.Graph(
            id="p3-G-1",
            figure=px.bar(data_frame="load_from_file_sepal_length", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(id="p3-F-1", column="sepal_length", selector=vm.Slider()),
        vm.Filter(id="p3-F-2", column="sepal_length", selector=vm.RangeSlider()),
        vm.Parameter(
            targets=["p3-G-1.x"],
            selector=vm.RadioItems(
                options=["species", "sepal_width"], value="species", title="Simple X-axis parameter"
            ),
        ),
    ],
)

page_4 = vm.Page(
    title="[TO BE DONE IN THE FOLLOW UP PR] Temporal dynamic selectors",
    components=[
        vm.Graph(
            id="p4-G-1",
            figure=px.bar(data_frame="load_from_file_date_column", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(id="p4-F-1", column="date_column", selector=vm.DatePicker(range=False)),
        vm.Filter(id="p4-F-2", column="date_column", selector=vm.DatePicker()),
        vm.Parameter(
            targets=["p4-G-1.x"],
            selector=vm.RadioItems(
                options=["species", "sepal_width"], value="species", title="Simple X-axis parameter"
            ),
        ),
    ],
)

page_5 = vm.Page(
    title="Parametrised dynamic selectors",
    components=[
        vm.Graph(
            id="p5-G-1",
            figure=px.bar(data_frame="load_from_file_species", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(id="p5-F-1", column="species", targets=["p5-G-1"], selector=vm.Checklist()),
        vm.Parameter(
            targets=[
                "p5-G-1.data_frame.parametrized_species",
                # TODO: Uncomment the following target and see the magic :D
                #  Is this the indicator that parameter.targets prop has to support 'target' definition without the '.'?
                # "p5-F-1.",
            ],
            selector=vm.Dropdown(
                options=["setosa", "versicolor", "virginica"], multi=True, title="Parametrized species"
            ),
        ),
        vm.Parameter(
            targets=[
                "p5-G-1.x",
                # TODO: Uncomment the following target and see the magic :D
                # "p5-F-1.",
            ],
            selector=vm.RadioItems(
                options=["species", "sepal_width"], value="species", title="Simple X-axis parameter"
            ),
        ),
    ],
)


page_6 = vm.Page(
    title="Page to test things out",
    components=[
        vm.Graph(id="graph_dynamic", figure=px.bar(data_frame="load_from_file", **BAR_CHART_CONF)),
        vm.Graph(
            id="graph_static",
            figure=px.scatter(data_frame=px.data.iris(), **SCATTER_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            id="filter_container_id",
            column=FILTER_COLUMN,
            targets=["graph_dynamic"],
            # targets=["graph_static"],
            # selector=vm.Dropdown(id="filter_id"),
            # selector=vm.Dropdown(id="filter_id", value=["setosa"]),
            # selector=vm.Checklist(id="filter_id"),
            # selector=vm.Checklist(id="filter_id", value=["setosa"]),
            # TODO-BUG: vm.Dropdown(multi=False) Doesn't work if value is cleared. The persistence storage become
            #  "null" and our placeholder component dmc.DateRangePicker can't process null value. It expects a value or
            #  a list of values.
            #  SOLUTION -> Create the "Universal Vizro placeholder component".
            #  TEMPORARY SOLUTION -> set clearable=False for the dynamic Dropdown(multi=False)
            # selector=vm.Dropdown(id="filter_id", multi=False),
            # selector=vm.Dropdown(id="filter_id", multi=False, value="setosa"),
            # selector=vm.RadioItems(id="filter_id"),
            # selector=vm.RadioItems(id="filter_id", value="setosa"),
            # selector=vm.Slider(id="filter_id"),
            # selector=vm.Slider(id="filter_id", value=5),
            # selector=vm.RangeSlider(id="filter_id"),
            # selector=vm.RangeSlider(id="filter_id", value=[5, 7]),
        ),
        vm.Parameter(
            targets=["graph_dynamic.x"],
            selector=vm.RadioItems(options=["species", "sepal_width"], title="Simple X-axis parameter"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[homepage, page_1, page_2, page_3, page_4, page_5, page_6])

if __name__ == "__main__":
    app = Vizro().build(dashboard)

    print("RUNNING\n")

    app.run(dev_tools_hot_reload=False)
