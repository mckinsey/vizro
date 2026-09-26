import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

df = px.data.iris()
df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
df["is_setosa"] = df["species"] == "setosa"

temporal_df = px.data.iris()
temporal_df["datetime_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(temporal_df), freq="h")
temporal_df["time_column"] = temporal_df["datetime_column"].dt.time

custom_scatter = px.scatter(
    data_frame=df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    custom_data=["species", "sepal_length", "date_column", "is_setosa"],
    hover_data=["species", "sepal_length", "date_column", "is_setosa"],
)

timepicker_scatter = px.scatter(
    data_frame=temporal_df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    custom_data=["time_column"],
    hover_data=["time_column"],
)


set_control_non_categorical_graph = vm.Page(
    title=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_PAGE_TITLE,
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.Graph(
                    id=cnst.SCATTER_SET_CONTROL_NON_CATEGORICAL,
                    figure=custom_scatter,
                    title="Click on points to set the filters below",
                    actions=[
                        set_control(control=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_SLIDER, value="sepal_length"),
                        set_control(control=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_RANGE_SLIDER, value="sepal_length"),
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_SINGLE, value="date_column"
                        ),
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_RANGE, value="date_column"
                        ),
                        set_control(control=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_SWITCH, value="is_setosa"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.Graph(
                            id=cnst.SCATTER_SET_CONTROL_NON_CATEGORICAL_TARGET,
                            figure=px.scatter(df, x="sepal_width", y="petal_length", color="species"),
                        ),
                    ],
                    controls=[
                        # Numeric-Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_SLIDER,
                            column="sepal_length",
                            selector=vm.Slider(),
                        ),
                        # Numeric-Range
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_RANGE_SLIDER,
                            column="sepal_length",
                            selector=vm.RangeSlider(),
                        ),
                        # Temporal-Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_SINGLE,
                            column="date_column",
                            selector=vm.DatePicker(
                                id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_SINGLE_ID, range=False
                            ),
                        ),
                        # Temporal-Range
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_RANGE,
                            column="date_column",
                            selector=vm.DatePicker(
                                id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_DATEPICKER_RANGE_ID, range=True
                            ),
                        ),
                        # Boolean Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_GRAPH_SWITCH,
                            column="is_setosa",
                            selector=vm.Switch(value=True),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

set_control_non_categorical_ag_grid = vm.Page(
    title=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_PAGE_TITLE,
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.AgGrid(
                    id=cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL,
                    figure=dash_ag_grid(df),
                    title="Click on row to set the filters below",
                    actions=[
                        set_control(control=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_SLIDER, value="sepal_length"),
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_RANGE_SLIDER, value="sepal_length"
                        ),
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_SINGLE, value="date_column"
                        ),
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_RANGE, value="date_column"
                        ),
                        set_control(control=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_SWITCH, value="is_setosa"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.Graph(
                            id=cnst.SCATTER_SET_CONTROL_NON_CATEGORICAL_TARGET_AG_GRID,
                            figure=px.scatter(df, x="sepal_width", y="petal_length", color="species"),
                        ),
                    ],
                    controls=[
                        # Numeric-Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_SLIDER,
                            column="sepal_length",
                            selector=vm.Slider(),
                        ),
                        # Numeric-Range
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_RANGE_SLIDER,
                            column="sepal_length",
                            selector=vm.RangeSlider(),
                        ),
                        # Temporal-Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_SINGLE,
                            column="date_column",
                            selector=vm.DatePicker(
                                id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_SINGLE_ID, range=False
                            ),
                        ),
                        # Temporal-Range
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_RANGE,
                            column="date_column",
                            selector=vm.DatePicker(
                                id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_DATEPICKER_RANGE_ID, range=True
                            ),
                        ),
                        # Boolean Single
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_AG_GRID_SWITCH, column="is_setosa", selector=vm.Switch()
                        ),
                    ],
                ),
            ],
        ),
    ],
)

set_control_non_categorical_timepicker_graph = vm.Page(
    title=cnst.SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_PAGE_TITLE,
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.Graph(
                    id=cnst.SCATTER_SET_CONTROL_NON_CATEGORICAL_TIMEPICKER,
                    figure=timepicker_scatter,
                    title="Click on points to set the time filter below",
                    actions=[
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_FILTER,
                            value="time_column",
                        ),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.AgGrid(
                            id=cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_TARGET,
                            figure=dash_ag_grid(temporal_df),
                        ),
                    ],
                    controls=[
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_FILTER,
                            column="time_column",
                            targets=[cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_TARGET],
                            selector=vm.TimePicker(id=cnst.SET_CONTROL_NON_CATEGORICAL_TIMEPICKER_GRAPH_ID, range=True),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

set_control_non_categorical_datetimepicker_ag_grid = vm.Page(
    title=cnst.SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_PAGE_TITLE,
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.AgGrid(
                    id=cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER,
                    figure=dash_ag_grid(temporal_df),
                    title="Click on row to set the datetime filter below",
                    actions=[
                        set_control(
                            control=cnst.SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_FILTER,
                            value="datetime_column",
                        ),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.AgGrid(
                            id=cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_TARGET,
                            figure=dash_ag_grid(temporal_df),
                        ),
                    ],
                    controls=[
                        vm.Filter(
                            id=cnst.SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_FILTER,
                            column="datetime_column",
                            targets=[cnst.AG_GRID_SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_TARGET],
                            selector=vm.DateTimePicker(
                                id=cnst.SET_CONTROL_NON_CATEGORICAL_DATETIMEPICKER_AG_GRID_ID, range=True
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)
