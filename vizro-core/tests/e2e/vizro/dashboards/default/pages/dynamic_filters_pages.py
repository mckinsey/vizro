from functools import partial

import e2e.vizro.constants as cnst
import pandas as pd
import yaml
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager

SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}
BAR_CHART_CONF = {
    "x": "species",
    "color": "species",
    "color_discrete_map": SPECIES_COLORS,
}


def load_from_file(filter_column=None, parametrized_species=None):
    df = px.data.iris()

    if parametrized_species:
        return df[df["species"].isin(parametrized_species)]

    with open(cnst.DYNAMIC_FILTERS_DATA_CONFIG) as file:
        data = yaml.safe_load(file)
        data = data or {}

    if filter_column == "species":
        final_df = pd.concat(
            objs=[
                df[df[filter_column] == "setosa"].head(data.get("setosa", 0)),
                df[df[filter_column] == "versicolor"].head(data.get("versicolor", 0)),
                df[df[filter_column] == "virginica"].head(data.get("virginica", 0)),
            ],
            ignore_index=True,
        )
    elif filter_column == "sepal_length":
        final_df = df[df[filter_column].between(data.get("min"), data.get("max"), inclusive="both")]
    else:
        raise ValueError("Invalid FILTER_COLUMN")

    return final_df


data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})

data_manager["load_from_file_species"] = partial(load_from_file, filter_column="species")
data_manager["load_from_file_species"].timeout = -1
data_manager["load_from_file_sepal_length"] = partial(load_from_file, filter_column="sepal_length")
data_manager["load_from_file_sepal_length"].timeout = -1


dynamic_filters_categorical_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    components=[
        vm.Graph(
            id=cnst.BOX_DYNAMIC_FILTERS_ID,
            figure=px.bar(data_frame="load_from_file_species", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
            column="species",
            selector=vm.Dropdown(),
        ),
        vm.Filter(
            id=cnst.DROPDOWN_DYNAMIC_FILTER_ID,
            column="species",
            selector=vm.Dropdown(multi=False),
        ),
        vm.Filter(id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, column="species", selector=vm.Checklist()),
        vm.Filter(
            id=cnst.RADIOITEMS_DYNAMIC_FILTER_ID,
            column="species",
            selector=vm.RadioItems(),
        ),
    ],
)

dynamic_filters_numerical_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    components=[
        vm.Graph(
            id=cnst.BAR_DYNAMIC_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_sepal_length", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SLIDER_DYNAMIC_FILTER_ID,
            column="sepal_length",
            selector=vm.Slider(step=0.5),
        ),
        vm.Filter(
            id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID,
            column="sepal_length",
            selector=vm.RangeSlider(step=0.5),
        ),
    ],
)
