import time
from datetime import datetime as dt_datetime
from datetime import time as dt_time
from functools import partial

import e2e.vizro.constants as cnst
import pandas as pd
import yaml
from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid

SPECIES_COLORS = {"setosa": "#097DFE", "versicolor": "#6F39E3", "virginica": "#05D0F0"}
BAR_CHART_CONF = {
    "x": "species",
    "color": "species",
    "color_discrete_map": SPECIES_COLORS,
}

_COUNTRY_YAML_KEYS = {
    "china": "China",
    "japan": "Japan",
    "brazil": "Brazil",
    "united_states": "United States",
}
_REGIONS = {
    "North": {
        "Canada",
        "United States",
        "Denmark",
        "Finland",
        "Norway",
        "Sweden",
        "Iceland",
        "Ireland",
        "United Kingdom",
    },
    "South": {
        "Argentina",
        "Brazil",
        "Australia",
        "New Zealand",
        "India",
        "China",
        "Japan",
    },
    "West": {
        "Mexico",
        "Germany",
        "France",
        "Spain",
        "Italy",
        "Nigeria",
        "Egypt",
    },
    "East": {
        "Poland",
        "Ethiopia",
        "Kenya",
        "Korea, Rep.",
        "Thailand",
        "Indonesia",
    },
}


def _parse_time(value: str) -> dt_time:
    return dt_datetime.strptime(value, "%H:%M:%S").time()


def _species_subset(df: pd.DataFrame, data: dict) -> pd.DataFrame:
    return pd.concat(
        objs=[
            df[df["species"] == "setosa"].head(data.get("setosa", 0)),
            df[df["species"] == "versicolor"].head(data.get("versicolor", 0)),
            df[df["species"] == "virginica"].head(data.get("virginica", 0)),
        ],
        ignore_index=True,
    )


def _gapminder_with_regions() -> pd.DataFrame:
    gapminder = px.data.gapminder().query("year == 2007").copy()
    gapminder["region"] = gapminder["country"].map({c: r for r, cs in _REGIONS.items() for c in cs})
    return gapminder


def load_from_file(filter_column=None, parametrized_species=None):
    time.sleep(0.25)  # for testing, to catch reloading of the chart
    df = px.data.iris()

    if parametrized_species:
        return df[df["species"].isin(parametrized_species)]

    with open(cnst.DYNAMIC_FILTERS_DATA_CONFIG) as file:
        data = yaml.safe_load(file)
        data = data or {}

    if filter_column == "species":
        final_df = _species_subset(df, data)
    elif filter_column == "is_setosa":
        final_df = _species_subset(df, data)
        final_df["is_setosa"] = final_df["species"] == "setosa"
    elif filter_column == "sepal_length":
        final_df = df[df[filter_column].between(data.get("min"), data.get("max"), inclusive="both")]
    elif filter_column == "date_column":
        df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
        date_min = pd.to_datetime(data["date_min"])
        date_max = pd.to_datetime(data["date_max"])
        final_df = df[df["date_column"].between(date_min, date_max, inclusive="both")]
    elif filter_column == "time_hh_mm_ss":
        df["time_hh_mm_ss"] = pd.to_datetime(
            pd.date_range(start="2024-03-05 08:00", periods=len(df), freq="30min")
        ).time
        time_min = _parse_time(data["time_min"])
        time_max = _parse_time(data["time_max"])
        final_df = df[df["time_hh_mm_ss"].apply(lambda value: time_min <= value <= time_max)]
    elif filter_column == "datetime_utc":
        df["datetime_utc"] = pd.date_range(start="2024-03-05 08:00", periods=len(df), freq="30min", tz="UTC")
        datetime_min = pd.to_datetime(data["datetime_min"], utc=True)
        datetime_max = pd.to_datetime(data["datetime_max"], utc=True)
        final_df = df[df["datetime_utc"].between(datetime_min, datetime_max, inclusive="both")]
    elif filter_column == "hierarchical":
        gapminder = _gapminder_with_regions()
        included_countries = [country for key, country in _COUNTRY_YAML_KEYS.items() if data.get(key, 0)]
        final_df = gapminder[gapminder["country"].isin(included_countries)]
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
data_manager["load_from_file_is_setosa"] = partial(load_from_file, filter_column="is_setosa")
data_manager["load_from_file_is_setosa"].timeout = -1
data_manager["load_from_file_time_hh_mm_ss"] = partial(load_from_file, filter_column="time_hh_mm_ss")
data_manager["load_from_file_time_hh_mm_ss"].timeout = -1
data_manager["load_from_file_datetime_utc"] = partial(load_from_file, filter_column="datetime_utc")
data_manager["load_from_file_datetime_utc"].timeout = -1
data_manager["load_from_file_hierarchical"] = partial(load_from_file, filter_column="hierarchical")
data_manager["load_from_file_hierarchical"].timeout = -1


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

dynamic_filters_switch_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_SWITCH_PAGE,
    components=[
        vm.Graph(
            id=cnst.BAR_DYNAMIC_SWITCH_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_is_setosa", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.SWITCH_DYNAMIC_FILTER_CONTROL_ID,
            column="is_setosa",
            targets=[cnst.BAR_DYNAMIC_SWITCH_FILTER_ID],
            selector=vm.Switch(id=cnst.SWITCH_DYNAMIC_FILTER_ID, value=True, title="Show setosa"),
        ),
    ],
)

dynamic_filters_temporal_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_TEMPORAL_PAGE,
    components=[
        vm.Graph(
            id=cnst.BAR_DYNAMIC_TIME_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_time_hh_mm_ss", **BAR_CHART_CONF),
        ),
        vm.Graph(
            id=cnst.BAR_DYNAMIC_DATETIME_FILTER_ID,
            figure=px.bar(data_frame="load_from_file_datetime_utc", **BAR_CHART_CONF),
        ),
    ],
    controls=[
        vm.Filter(
            column="time_hh_mm_ss",
            targets=[cnst.BAR_DYNAMIC_TIME_FILTER_ID],
            selector=vm.TimePicker(id=cnst.TIMEPICKER_DYNAMIC_FILTER_ID, title="Dynamic time"),
        ),
        vm.Filter(
            column="datetime_utc",
            targets=[cnst.BAR_DYNAMIC_DATETIME_FILTER_ID],
            selector=vm.DateTimePicker(id=cnst.DATETIMEPICKER_DYNAMIC_FILTER_ID, title="Dynamic datetime"),
        ),
    ],
)

dynamic_filters_cascader_page = vm.Page(
    title=cnst.DYNAMIC_FILTERS_CASCADER_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.AG_GRID_DYNAMIC_CASCADER_ID,
            figure=dash_ag_grid(data_frame="load_from_file_hierarchical"),
        ),
    ],
    controls=[
        vm.Filter(
            column=["continent", "region", "country"],
            targets=[cnst.AG_GRID_DYNAMIC_CASCADER_ID],
            selector=vm.Cascader(
                id=cnst.CASCADER_DYNAMIC_FILTER_ID,
                multi=False,
                full_path=False,
                value="United States",
                title="Country (dynamic)",
            ),
        ),
    ],
)
