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
_rand_time_base = pd.Series(pd.to_datetime(_rng.integers(0, 24 * 60 * 60, size=_n), unit="s"))

dff = pd.DataFrame(
    {
        # "datetime" type — filterable by DatePicker (date) or TimePicker (time-of-day)
        "datetime_utc": _datetime_utc,
        # "time" type — time_iso includes microseconds from datetime_utc
        "time_iso": _datetime_utc.dt.time,  # hh:mm:ss.xxxxxx (microsecond precision)
        # "time" type — independent random time-of-day values
        "time_hh_mm_ss": _rand_time_base.dt.time,  # hh:mm:ss
    }
)


timepicker_range = vm.Page(
    title=cnst.TIMEPICKER_RANGE_PAGE,
    components=[vm.AgGrid(id=cnst.TIMEPICKER_RANGE_AG_GRID_ID, figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(column="datetime_utc"),
        vm.Filter(
            column="datetime_utc",
            selector=vm.TimePicker(id=cnst.TIMEPICKER_DATETIME_UTC_TIME_RANGE_ID, title="datetime_utc time"),
        ),
        vm.Filter(
            column="time_iso",
            selector=vm.TimePicker(id=cnst.TIMEPICKER_TIME_ISO_RANGE_ID, title="time_iso"),
        ),
        # show_in_url=True uses the Filter id (not the TimePicker selector id) in the URL query string
        vm.Filter(
            id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_FILTER_CONTROL_ID,
            column="time_hh_mm_ss",
            show_in_url=True,
            selector=vm.TimePicker(id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID, title="time_hh_mm_ss"),
        ),
    ],
)


timepicker_single = vm.Page(
    title=cnst.TIMEPICKER_SINGLE_PAGE,
    components=[vm.AgGrid(id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID, figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(column="datetime_utc"),
        vm.Filter(
            column="datetime_utc",
            selector=vm.TimePicker(
                id=cnst.TIMEPICKER_DATETIME_UTC_TIME_SINGLE_ID, title="datetime_utc time", range=False
            ),
        ),
        vm.Filter(
            column="time_iso",
            selector=vm.TimePicker(id=cnst.TIMEPICKER_TIME_ISO_SINGLE_ID, title="time_iso", range=False),
        ),
        vm.Filter(
            column="time_hh_mm_ss",
            selector=vm.TimePicker(id=cnst.TIMEPICKER_TIME_HH_MM_SS_SINGLE_ID, title="time_hh_mm_ss", range=False),
        ),
    ],
)

timepicker_parameter = vm.Page(
    title=cnst.TIMEPICKER_PARAMETER_PAGE,
    components=[
        vm.Graph(
            id=cnst.TIMEPICKER_PARAMETER_SCATTER_ID,
            figure=px.scatter(
                px.data.iris(), title="My scatter chart", x="sepal_length", y="petal_width", color="species"
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[f"{cnst.TIMEPICKER_PARAMETER_SCATTER_ID}.title"],
            selector=vm.TimePicker(id=cnst.TIMEPICKER_PARAMETER_ID, range=False),
        ),
    ],
)
