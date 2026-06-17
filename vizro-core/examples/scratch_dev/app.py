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
        # Pure-date columns (all midnight — "date" type, DatePicker only)
        "date_yyyy_mm_dd": pd.Series(_date_range_2026[_rng.integers(0, len(_date_range_2026), size=_n)]),
        # Time-of-day columns ("time" type, TimePicker only)
        "time_iso": _datetime_utc.dt.time,  # hh:mm:ss.xxxxxx (microsecond precision)
        "time_hh_mm_ss": _rand_time_base.dt.time,  # hh:mm:ss
        "time_hh_mm": _rand_time_base.dt.floor("min").dt.time,  # hh:mm (second=0)
    }
)


page_0 = vm.Page(
    title="Range Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        # datetime_utc — "datetime" type: tested as date (DatePicker) and time-of-day (TimePicker)
        vm.Filter(column="datetime_utc"),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DatePicker(title="datetime_utc date + value", value=["2026-01-03", "2026-12-29"]),
        ),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time")),
        vm.Filter(
            column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time + value", value=["00:00", "23:59"])
        ),
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
            selector=vm.TimePicker(title="time_hh_mm_ss time+ + value", value=["00:00", "23:59"]),
        ),
        vm.Filter(column="time_hh_mm"),
    ],
)

page_1 = vm.Page(
    title="Single Pickers",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=dff))],
    controls=[
        # datetime_utc — tested as date (DatePicker) and time-of-day (TimePicker)
        vm.Filter(column="datetime_utc", selector=vm.DatePicker(title="datetime_utc date", range=False)),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DatePicker(title="datetime_utc date + value", range=False, value="2026-03-01"),
        ),
        vm.Filter(column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time", range=False)),
        vm.Filter(
            column="datetime_utc", selector=vm.TimePicker(title="datetime_utc time + value", range=False, value="00:00")
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

page_2 = vm.Page(
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
    ],
)

page_3 = vm.Page(
    title="Time as Parameter",
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
            selector=vm.TimePicker(range=False),
        ),
    ],
)


from vizro.models.types import capture

vm.Page.add_type("controls", vm.RadioItems)


@capture("action")
def update_time_pickers(radio_items_value: str):
    if radio_items_value == "Both shifts":
        return "", ""
    elif radio_items_value == "First shift":
        return "08:00", "20:00"
    elif radio_items_value == "Second shift":
        return "20:00", "08:00"


page_4 = vm.Page(
    title="Coda example",
    components=[
        vm.AgGrid(figure=dash_ag_grid(data_frame=dff)),
    ],
    controls=[
        vm.Filter(column="datetime_utc"),
        # vm.RadioItems(
        #     id="radio_items_id",
        #     options=["Both shifts", "First shift", "Second shift"],
        #     value="Both shifts",
        #     actions=vm.Action(
        #         function=update_time_pickers("radio_items_id"),
        #         outputs=["time_picker_id-start.value", "time_picker_id-end.value"],
        #     ),
        # ),
        vm.Filter(
            # visible=False,
            column="time_hh_mm_ss",
            selector=vm.TimePicker(
                title='Filter "time_hh_mm_ss" column:',
                description="Input start and end time to filter results by time_hh_mm_ss column.",
                id="time_picker_id",
                extra=dict(
                    withSeconds=True,
                    withDropdown=True,
                    presets=[
                        {"label": "08am -> 08pm (first shift)", "values": ["08:00:00"]},
                        {"label": "08pm -> 08am (second shift)", "values": ["20:00:00"]},
                    ],
                ),
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

# "hour" column is integer
tips["hour"] = clock.hour
# "clock_time" is in format HH:MM:SS
tips["clock_time"] = clock.time
tips = tips.sort_values("clock_time").reset_index(drop=True)

page_5 = vm.Page(
    title="Time Pickers",
    components=[
        vm.Graph(
            figure=px.histogram(
                tips,
                x="hour",
                y="tip",
                color="time",
                histfunc="sum",
                title="Summarized tip by hour of day",
                labels={"hour": "Hour of day", "tip": "Summarized tip ($)", "time": "Meal"},
            ),
        ),
        vm.AgGrid(title="Row Data", figure=dash_ag_grid(data_frame=tips)),
    ],
    controls=[
        vm.Filter(column="clock_time", selector=vm.TimePicker(title="Lunch/Dinner - time range")),
        vm.Filter(column="clock_time", selector=vm.TimePicker(title="Lunch/Dinner - time", range=False)),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        # page_0,
        page_1,
        page_2,
        page_3,
        page_4,
        page_5,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
