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
dff["time_hh_mm_ss"] = dff["datetime_utc"].dt.strftime("%H:%M:%S")

# TODO NOW PP: Test if only time-column works
# TODO NOW PP: Fix ResetControls
# TODO NOW PP: Test URL
# TODO NOW PP: Test Parameter
# TODO NOW PP: Check what's all added in the Cascader PR.
# TODO NOW PP: Fix existing tests and write unit tests
# TODO NOW PP OQ: Should we revert this to `"rowData": data_frame.to_dict("records")`?
# TODO NOW PP: Fix UI
# TODO NOW PP: Docs
# TODO NOW PP: e2e - call with Alexey

page = vm.Page(
    title="Time Picker",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=dff))
    ],
    controls=[
        vm.Filter(column="datetime_utc"),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker()),
        # vm.Filter(column="time_hh_mm_ss", selector=vm.TimePicker()),
    ],
)

dashboard = vm.Dashboard(
    pages=[page],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
