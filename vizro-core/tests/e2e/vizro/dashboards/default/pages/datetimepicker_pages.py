import e2e.vizro.constants as cnst
import numpy as np
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

# Fixed seed so row counts in e2e tests are deterministic across dashboard restarts.
_rng = np.random.default_rng(42)
_n = 365

_datetime_utc = pd.Series(
    pd.to_datetime(
        _rng.integers(
            pd.Timestamp("2026-01-01", tz="UTC").value,
            pd.Timestamp("2026-12-31 23:59:59", tz="UTC").value,
            size=_n,
        ),
        utc=True,
    )
)

dff = pd.DataFrame(
    {
        # "datetime" type - filterable by DatePicker (date) (default), DateTimePicker (date + time) or TimePicker (time)
        "datetime_utc": _datetime_utc,
    }
)


datetimepicker_range = vm.Page(
    title=cnst.DATETIMEPICKER_RANGE_PAGE,
    components=[vm.AgGrid(id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID, figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(
                id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
                title="datetime_utc datetime",
            ),
        ),
    ],
)


datetimepicker_range_url = vm.Page(
    title=cnst.DATETIMEPICKER_RANGE_URL_PAGE,
    components=[vm.AgGrid(id=cnst.DATETIMEPICKER_RANGE_URL_AG_GRID_ID, figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(
            id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_FILTER_CONTROL_ID,
            column="datetime_utc",
            show_in_url=True,
            selector=vm.DateTimePicker(
                id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_URL_ID,
                title="datetime_utc datetime url",
            ),
        ),
    ],
)


datetimepicker_single = vm.Page(
    title=cnst.DATETIMEPICKER_SINGLE_PAGE,
    components=[vm.AgGrid(id=cnst.DATETIMEPICKER_SINGLE_AG_GRID_ID, figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(column="datetime_utc"),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(
                id=cnst.DATETIMEPICKER_DATETIME_UTC_SINGLE_ID, title="datetime_utc datetime", range=False
            ),
        ),
    ],
)


datetimepicker_parameter = vm.Page(
    title=cnst.DATETIMEPICKER_PARAMETER_PAGE,
    components=[
        vm.Graph(
            id=cnst.DATETIMEPICKER_PARAMETER_SCATTER_ID,
            figure=px.scatter(
                px.data.iris(), title="My scatter chart", x="sepal_length", y="petal_width", color="species"
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.DATETIMEPICKER_PARAMETER_SCATTER_ID}.title"],
            selector=vm.DateTimePicker(
                id=cnst.DATETIMEPICKER_PARAMETER_ID, min="2026-01-01", max="2026-02-02", range=False
            ),
        ),
    ],
)
