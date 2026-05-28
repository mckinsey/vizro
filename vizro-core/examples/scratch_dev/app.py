"""Scratch demo app"""

import pandas as pd
import numpy as np

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro
from vizro.tables import dash_ag_grid


dff = px.data.iris()
dff["datetime_utc"] = pd.to_datetime(
    np.random.default_rng(42).integers(
        pd.Timestamp("2026-01-01", tz="UTC").value,
        pd.Timestamp("2026-12-31 23:59:59", tz="UTC").value,
        size=len(dff),
    ),
    utc=True,
)

dff["time_iso"] = dff["datetime_utc"].dt.time

dff["time_hh_mm_ss"] = pd.to_datetime(
    np.random.randint(0, 24 * 60 * 60, size=len(dff)),
    unit="s"
).time

dff.pop("petal_width")
dff.pop("petal_length")

# TODO NOW PP: TimePicker Single doesn't work with ISO seconds due to difference in the milliseconds.
# TODO NOW PP: Check what's all added in the Cascader PR.
# TODO NOW PP: Fix existing tests and write unit tests
# TODO NOW PP OQ: Should we revert this to `"rowData": data_frame.to_dict("records")`?
# TODO NOW PP: Configure selectors with extra to cover CODA use case
# TODO NOW PP: Fix UI (add clock, remove seconds, if range move the end picker to the float right)
# TODO NOW PP: Call Li/Steph about the UI.
# TODO NOW PP: Docs
# TODO NOW PP: e2e - call with Alexey

page_0 = vm.Page(
    title="Range Time Picker",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=dff))
    ],
    controls=[
        vm.Filter(column="datetime_utc"),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker()),
        vm.Filter(column="time_iso"),
        vm.Filter(column="time_hh_mm_ss"),
    ],
)

page_1 = vm.Page(
    title="Single Time Picker",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=dff))
    ],
    controls=[
        vm.Filter(column="datetime_utc", selector=vm.DatePicker(range=False)),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(range=False)),
        vm.Filter(column="time_iso", selector=vm.TimePicker(range=False)),
        vm.Filter(column="time_hh_mm_ss", selector=vm.TimePicker(range=False)),
    ],
)


page_2 = vm.Page(
    title="Time in URL (test reset)",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=dff)),
    ],
    controls=[
        vm.Filter(column="datetime_utc", id="filter_1", selector=vm.TimePicker(id="filter_selector_1"), show_in_url=True),
        vm.Filter(column="time_iso", id="filter_2", selector=vm.TimePicker(id="filter_selector_2"), show_in_url=True),
        vm.Filter(column="time_hh_mm_ss", id="filter_3", selector=vm.TimePicker(id="filter_selector_3", range=False), show_in_url=True),
    ]
)

page_3 = vm.Page(
    title="Time as Parameter",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(px.data.iris(), title="My scatter chart", x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_chart.title"],
            selector=vm.TimePicker(range=False),
        ),
    ]
)

dashboard = vm.Dashboard(
    pages=[
        page_0,
        page_1,
        page_2,
        page_3,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
