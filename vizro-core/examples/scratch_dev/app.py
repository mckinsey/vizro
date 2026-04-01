"""Dev app to try things out."""

import pandas as pd
from dash import ctx, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.actions import set_control
from vizro.tables import dash_ag_grid
from typing import Literal
import json

df = px.data.iris()
df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
df["is_setosa"] = df["species"] == "setosa"

custom_scatter = px.scatter(
    data_frame=df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    custom_data=["species", "sepal_length", "date_column", "is_setosa"],
    hover_data=["species", "sepal_length", "date_column", "is_setosa"],
)


page_1 = vm.Page(
    title="Graph targets different selectors",
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.Graph(
                    figure=custom_scatter,
                    title="Click on points to set the filters below",
                    actions=[
                        set_control(control="p8_filter_click_1", value="species"),
                        set_control(control="p8_filter_click_2", value="species"),
                        set_control(control="p8_filter_click_3", value="species"),
                        set_control(control="p8_filter_click_4", value="species"),
                        set_control(control="p8_filter_click_5", value="sepal_length"),
                        set_control(control="p8_filter_click_6", value="sepal_length"),
                        set_control(control="p8_filter_click_7", value="date_column"),
                        set_control(control="p8_filter_click_8", value="date_column"),
                        set_control(control="p8_filter_click_9", value="is_setosa"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                    ],
                    controls=[
                        # Categorical-Single
                        vm.Filter(id="p8_filter_click_1", column="species", selector=vm.RadioItems()),
                        vm.Filter(id="p8_filter_click_2", column="species", selector=vm.Dropdown(multi=False)),
                        # # Categorical-Multi
                        vm.Filter(id="p8_filter_click_3", column="species", selector=vm.Checklist()),
                        vm.Filter(id="p8_filter_click_4", column="species", selector=vm.Dropdown()),
                        # Numeric-Single
                        vm.Filter(id="p8_filter_click_5", column="sepal_length", selector=vm.Slider()),
                        # Numeric-Range
                        vm.Filter(id="p8_filter_click_6", column="sepal_length", selector=vm.RangeSlider()),
                        # Temporal-Single
                        vm.Filter(id="p8_filter_click_7", column="date_column", selector=vm.DatePicker(range=False)),
                        # # Temporal-Range
                        vm.Filter(id="p8_filter_click_8", column="date_column", selector=vm.DatePicker(range=True)),
                        # Boolean Single
                        vm.Filter(id="p8_filter_click_9", column="is_setosa", selector=vm.Switch()),
                    ],
                ),
            ],
        ),
    ],
)

page_2 = vm.Page(
    title="AgGrid targets different selectors",
    components=[
        vm.Container(
            title="Click set_control",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(df),
                    title="Click on row to set the filters below",
                    actions=[
                        set_control(control="p9_filter_click_1", value="species"),
                        set_control(control="p9_filter_click_2", value="species"),
                        set_control(control="p9_filter_click_3", value="species"),
                        set_control(control="p9_filter_click_4", value="species"),
                        set_control(control="p9_filter_click_5", value="sepal_length"),
                        set_control(control="p9_filter_click_6", value="sepal_length"),
                        set_control(control="p9_filter_click_7", value="date_column"),
                        set_control(control="p9_filter_click_8", value="date_column"),
                        set_control(control="p9_filter_click_9", value="is_setosa"),
                    ],
                ),
                vm.Container(
                    components=[
                        vm.Graph(figure=px.scatter(df, x="sepal_width", y="petal_length", color="species")),
                    ],
                    controls=[
                        vm.Filter(id="p9_filter_click_1", column="species", selector=vm.RadioItems()),
                        vm.Filter(id="p9_filter_click_2", column="species", selector=vm.Dropdown(multi=False)),
                        vm.Filter(id="p9_filter_click_3", column="species", selector=vm.Checklist()),
                        vm.Filter(id="p9_filter_click_4", column="species", selector=vm.Dropdown()),
                        vm.Filter(id="p9_filter_click_5", column="sepal_length", selector=vm.Slider()),
                        vm.Filter(id="p9_filter_click_6", column="sepal_length", selector=vm.RangeSlider()),
                        vm.Filter(id="p9_filter_click_7", column="date_column", selector=vm.DatePicker(range=False)),
                        vm.Filter(id="p9_filter_click_8", column="date_column", selector=vm.DatePicker(range=True)),
                        vm.Filter(id="p9_filter_click_9", column="is_setosa", selector=vm.Switch()),
                    ],
                ),
            ],
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[page_1],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
