import time
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
    time.sleep(0.25)  # for testing, to catch reloading of the chart
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
    elif filter_column == "date_column":
        df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
        date_min = pd.to_datetime(data["date_min"])
        date_max = pd.to_datetime(data["date_max"])
        final_df = df[df["date_column"].between(date_min, date_max, inclusive="both")]
    else:
        raise ValueError("Invalid FILTER_COLUMN")

    return final_df


data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})

data_manager["load_from_file_species"] = partial(load_from_file, filter_column="species")
data_manager["load_from_file_species"].timeout = -1
data_manager["load_from_file_sepal_length"] = partial(load_from_file, filter_column="sepal_length")
data_manager["load_from_file_sepal_length"].timeout = -1
data_manager["load_from_file_date_column"] = partial(load_from_file, filter_column="date_column")
data_manager["load_from_file_date_column"].timeout = -1


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
            column="species",
            selector=vm.Dropdown(id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID),
        ),
        vm.Filter(
            column="species",
            selector=vm.Dropdown(id=cnst.DROPDOWN_DYNAMIC_FILTER_ID, multi=False),
        ),
        vm.Filter(column="species", selector=vm.Checklist(id=cnst.CHECKLIST_DYNAMIC_FILTER_ID)),
        vm.Filter(
            column="species",
            selector=vm.RadioItems(id=cnst.RADIOITEMS_DYNAMIC_FILTER_ID),
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
            column="sepal_length",
            selector=vm.Slider(id=cnst.SLIDER_DYNAMIC_FILTER_ID, step=0.5),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.RangeSlider(id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID, step=0.5),
        ),
    ],
)

dynamic_filters_datepicker_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    components=[
        vm.Graph(
            id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_date_column", **BAR_CHART_CONF),
        ),
        vm.Graph(
            id=cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_date_column", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        # Dynamic Single
        vm.Filter(
            column="date_column",
            targets=[cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID],
            selector=vm.DatePicker(id=cnst.DATEPICKER_DYNAMIC_SINGLE_ID, title="Dynamic Single", range=False),
        ),
        # Dynamic Multi
        vm.Filter(
            column="date_column",
            targets=[cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID],
            selector=vm.DatePicker(id=cnst.DATEPICKER_DYNAMIC_RANGE_ID, title="Dynamic Multi"),
        ),
    ],
)
