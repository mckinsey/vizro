"""Scratch demo app"""

import pandas as pd
import numpy as np

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro
from vizro.tables import dash_ag_grid


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
_date_range_2026 = pd.date_range("2026-01-01", "2026-12-31", freq="D")

dff = pd.DataFrame(
    {
        "datetime_utc": _datetime_utc,
        # Same data, tz-naive — exercises DateTimePicker without hitting tz-localization in _coerce_temporal
        "datetime_naive": _datetime_utc.dt.tz_localize(None),
        # Pure-date columns (all midnight — "date" type, DatePicker only)
        "date_yyyy_mm_dd": pd.Series(_date_range_2026[_rng.integers(0, len(_date_range_2026), size=_n)]),
        # Time-of-day columns ("time" type, TimePicker only)
        "time_iso": _datetime_utc.dt.time,  # hh:mm:ss.xxxxxx (microsecond precision)
        "time_hh_mm_ss": _rand_time_base.dt.time,  # hh:mm:ss
        "time_hh_mm": _rand_time_base.dt.floor("min").dt.time,  # hh:mm (second=0)
    }
)

page_0 = vm.Page(
    title="TLDR: Range Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(
            column="datetime_utc",
            selector=vm.DatePicker(title="range DatePicker", value=["2026-01-03", "2026-12-29"]),
        ),
        vm.Filter(
            column="time_hh_mm_ss",
            selector=vm.TimePicker(title="range TimePicker", value=["00:00", "23:59"]),
        ),
        vm.Filter(column="datetime_utc", selector=vm.DateTimePicker(title="range DateTimePicker")),
    ],
)

page_1 = vm.Page(
    title="TLDR: Single Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        vm.Filter(column="datetime_utc", selector=vm.DatePicker(title="single DatePicker", range=False)),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(title="single TimePicker", range=False)),
        vm.Filter(column="datetime_utc", selector=vm.DateTimePicker(title="single DateTimePicker", range=False)),
    ],
)

page_2 = vm.Page(
    title="Detailed: Range Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        # datetime_utc — "datetime" type: tested as date (DatePicker), time-of-day (TimePicker), and datetime (DateTimePicker)
        vm.Filter(column="datetime_utc"),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DatePicker(title="range DatePicker", value=["2026-01-03", "2026-12-29"]),
        ),
        vm.Filter(
            column="time_hh_mm_ss",
            selector=vm.TimePicker(title="range TimePicker", value=["00:00", "23:59"]),
        ),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time")),
        vm.Filter(
            column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time + value", value=["00:00", "23:59"])
        ),
        vm.Filter(column="datetime_utc", selector=vm.DateTimePicker(title="range DateTimePicker")),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(
                title="datetime_utc datetime + value",
                value=["2026-01-03T08:00", "2026-12-29T20:00"],
            ),
        ),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(
                title="datetime_utc datetime + min/max",
                min="2026-01-01",
                max="2026-12-31",
            ),
        ),
        # datetime_naive — "datetime" type (tz-naive variant for the simpler coercion path)
        vm.Filter(column="datetime_naive", selector=vm.DateTimePicker(title="datetime_naive datetime")),
        # date columns — DatePicker only
        vm.Filter(column="date_yyyy_mm_dd"),
        vm.Filter(
            column="date_yyyy_mm_dd",
            selector=vm.DatePicker(title="date_yyyy_mm_dd date + value", value=["2026-01-03", "2026-12-29"]),
        ),
        # time columns — TimePicker only
        vm.Filter(column="time_iso"),
        vm.Filter(
            column="time_hh_mm_ss",
            selector=vm.TimePicker(title="time_hh_mm_ss time-picker + value", value=["00:00", "23:59"]),
        ),
        vm.Filter(column="time_hh_mm"),
    ],
)

page_3 = vm.Page(
    title="Detailed: Single Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        # datetime_utc — tested as date (DatePicker), time-of-day (TimePicker), and datetime (DateTimePicker)
        vm.Filter(column="datetime_utc", selector=vm.DatePicker(title="single DatePicker", range=False)),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DatePicker(title="datetime_utc date + value", range=False, value="2026-03-01"),
        ),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(title="single TimePicker", range=False)),
        vm.Filter(
            column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time + value", range=False, value="00:00")
        ),
        vm.Filter(column="datetime_utc", selector=vm.DateTimePicker(title="single DateTimePicker", range=False)),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(title="datetime_utc datetime + value", range=False, value="2026-03-01T08:00"),
        ),
        # datetime_naive — tz-naive single DateTimePicker
        vm.Filter(
            column="datetime_naive",
            selector=vm.DateTimePicker(title="datetime_naive datetime", range=False),
        ),
        # date columns
        vm.Filter(column="date_yyyy_mm_dd", selector=vm.DatePicker(title="date_yyyy_mm_dd", range=False)),
        vm.Filter(
            column="date_yyyy_mm_dd",
            selector=vm.DatePicker(title="date_yyyy_mm_dd + value", range=False, value="2026-03-01"),
        ),
        # time columns
        vm.Filter(column="time_iso", selector=vm.TimePicker(title="time_iso", range=False)),
        vm.Filter(
            column="time_hh_mm_ss", selector=vm.TimePicker(title="time_hh_mm_ss + value", range=False, value="00:00")
        ),
        vm.Filter(column="time_hh_mm", selector=vm.TimePicker(title="time_hh_mm", range=False)),
    ],
)

page_4 = vm.Page(
    title="Filters in URL",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        # Range filters (from page_0)
        vm.Filter(
            column="datetime_utc",
            id="filter_dt_date_range",
            selector=vm.DatePicker(id="dp_dt_range", title="datetime_utc date range"),
            show_in_url=True,
        ),
        vm.Filter(
            column="datetime_utc",
            id="filter_dt_time_range",
            selector=vm.TimePicker(id="tp_dt_range", title="datetime_utc time range + value", value=["08:00", "20:00"]),
            show_in_url=True,
        ),
        vm.Filter(
            column="time_iso",
            id="filter_time_iso_range",
            selector=vm.TimePicker(id="tp_time_iso", title="time_iso range"),
            show_in_url=True,
        ),
        vm.Filter(
            column="datetime_utc",
            id="filter_dt_datetime_range",
            selector=vm.DateTimePicker(
                id="dtp_dt_range",
                title="datetime_utc datetime range + value",
                value=["2026-03-01T08:00", "2026-09-30T20:00"],
            ),
            show_in_url=True,
        ),
        # Single filters (from page_1)
        vm.Filter(
            column="datetime_utc",
            id="filter_dt_time_single",
            selector=vm.TimePicker(id="tp_dt_single", title="datetime_utc time single", range=False),
            show_in_url=True,
        ),
        vm.Filter(
            column="date_yyyy_mm_dd",
            id="filter_date_yyyy_single",
            selector=vm.DatePicker(
                id="dp_date_yyyy", title="date_yyyy_mm_dd single + value", range=False, value="2026-03-01"
            ),
            show_in_url=True,
        ),
        vm.Filter(
            column="time_hh_mm",
            id="filter_time_hh_mm_single",
            selector=vm.TimePicker(id="tp_hh_mm", title="time_hh_mm single", range=False),
            show_in_url=True,
        ),
        vm.Filter(
            column="datetime_utc",
            id="filter_dt_datetime_single",
            selector=vm.DateTimePicker(id="dtp_dt_single", title="datetime_utc datetime single", range=False),
            show_in_url=True,
        ),
    ],
)

page_5 = vm.Page(
    title="DateTime as Parameter",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(
                px.data.iris(), title="My scatter chart", x="sepal_length", y="petal_width", color="species"
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_chart.title"],
            selector=vm.DateTimePicker(
                min="2026-01-01",
                max="2026-02-02",
                range=False,
            ),
        ),
    ],
)


# Build a clock_time per row inside the Lunch/Dinner window of the original "time" (Lunch/Dinner) column.
tips = px.data.tips()
# Assign random clock_time to match Lunch and Dinner "time" column
windows = {"Lunch": (12 * 3600, 17 * 3600), "Dinner": (17 * 3600, 24 * 3600)}
starts = tips["time"].map(lambda x: windows[x][0])
ends = tips["time"].map(lambda x: windows[x][1])
clock = pd.to_datetime(_rng.integers(starts, ends), unit="s")

# "clock_time" is in format HH:MM:SS
tips["clock_time"] = clock.time
tips = tips.sort_values("clock_time").reset_index(drop=True)

page_8 = vm.Page(
    title="DateTime Pickers",
    components=[
        vm.Graph(
            figure=px.histogram(
                dff,
                x="datetime_naive",
                title="Records by datetime",
                labels={"datetime_naive": "Datetime"},
            ),
        ),
        vm.AgGrid(title="Row Data", figure=dash_ag_grid(data_frame=dff)),
    ],
    controls=[
        vm.Filter(column="datetime_naive", selector=vm.DateTimePicker(title="Datetime range")),
        vm.Filter(column="datetime_naive", selector=vm.DateTimePicker(title="Datetime single", range=False)),
    ],
)

# Build a full "order_datetime" per row: spread orders across a two-week window and attach the
# clock time-of-day, so the newly added column is a real "datetime" (date + time) type.
_order_date = pd.Series(
    pd.to_datetime("2026-06-01") + pd.to_timedelta(_rng.integers(0, 14, size=len(tips)), unit="D")
).dt.normalize()
# "order_datetime" is a datetime64 column (date + time), filterable with DateTimePicker.
# Drop the helper "size"/"clock_time" columns so the page shows a clean datetime-focused table.
tips_orders = tips.drop(columns=["size", "clock_time"])
tips_orders["order_datetime"] = pd.to_datetime(
    _order_date.dt.strftime("%Y-%m-%d") + " " + tips["clock_time"].astype(str)
)
tips_orders = tips_orders.sort_values("order_datetime").reset_index(drop=True)

page_9 = vm.Page(
    title="DateTime Pickers (orders)",
    components=[
        vm.Graph(
            figure=px.histogram(
                tips_orders,
                x="order_datetime",
                y="tip",
                color="time",
                histfunc="sum",
                title="Summarized tip by order date-time",
                labels={"order_datetime": "Order date-time", "tip": "Summarized tip ($)", "time": "Meal"},
            ),
        ),
        vm.AgGrid(title="Row Data", figure=dash_ag_grid(data_frame=tips_orders)),
    ],
    controls=[
        vm.Filter(column="order_datetime", selector=vm.DateTimePicker(title="Lunch/Dinner - date-time range")),
        vm.Filter(column="order_datetime", selector=vm.DateTimePicker(title="Lunch/Dinner - date-time", range=False)),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_0,
        page_1,
        page_2,
        page_3,
        page_4,
        page_5,
        page_8,
        page_9,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
