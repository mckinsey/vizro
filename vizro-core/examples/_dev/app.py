"""Example to show dashboard configuration."""

import datetime
import random

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

vm.Page.add_type("components", vm.DatePicker)

date_data_frame = pd.DataFrame(
    {
        "value": [random.randint(0, 5) for _ in range(31)],
        "time": [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)],
        "type": [random.choice(["A", "B", "C"]) for _ in range(31)],
    }
)

numerical_selectors = [
    vm.RangeSlider(id="numerical_range_slider"),
    vm.Slider(id="numerical_slider"),
    vm.Dropdown(id="numerical_dropdown"),
    vm.RadioItems(id="numerical_radio_items"),
    vm.Checklist(id="numerical_checklist"),
    # vm.DatePicker(id="numerical_date_picker")  # -> doesn't work properly with numerical column_type
    #    because it's impossible to compare "number" with "date"
]

temporal_selectors = [
    # vm.RangeSlider(id="temporal_range_slider"),  # -> dcc.RangeSlider doesn't work with temporal data
    # vm.Slider(id="temporal_slider"),  # -> dcc.Slider doesn't work with temporal data
    vm.Dropdown(id="temporal_dropdown"),
    vm.RadioItems(id="temporal_radio_items"),
    vm.Checklist(id="temporal_checklist"),
    vm.DatePicker(id="temporal_date_picker"),
]

categorical_selectors = [
    # vm.RangeSlider(id="categorical_range_slider"),  # -> dcc.RangeSlider doesn't work with categorical data
    # vm.Slider(id="categorical_slider"),  # -> dcc.Slider doesn't work with categorical data
    vm.Dropdown(id="categorical_dropdown"),
    vm.RadioItems(id="categorical_radio_items"),
    vm.Checklist(id="categorical_checklist"),
    # vm.DatePicker(id="categorical_date_picker")  # -> dmc.DatePicker doesn't work with categorical data
]

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.line(date_data_frame, x="time", y="value")),
        vm.DatePicker(min="2024-01-01", max="2026-01-01", range=False),
    ],
    controls=[
        # *[vm.Filter(column="value", selector=selector) for selector in numerical_selectors],
        # *[vm.Filter(column="time", selector=selector) for selector in temporal_selectors],
        # *[vm.Filter(column="type", selector=selector) for selector in categorical_selectors],
        vm.Filter(column="type"),
        vm.Filter(column="value"),
        vm.Filter(column="time"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
