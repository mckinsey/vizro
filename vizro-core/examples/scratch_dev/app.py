"""Manual test app for the dynamic DateTimePicker (date portion).

What to try:
  * The two DateTimePicker filters on the left are DYNAMIC: their date `min`/`max` are NOT set, and the
    `timeseries` data source is a function, so the pickers' selectable date bounds track the data.
  * Drag the two `Parameter` sliders (they are data_frame parameters you set manually at runtime):
      - "Start offset (days)" shifts the first row forward  -> the pickers' EARLIEST selectable date moves up.
      - "Number of days"      lengthens the series          -> the pickers' LATEST selectable date extends.
    After each change the filters reload and the DatePickerInput min/max update, while your selected value
    is preserved (the bounds widen to keep it valid if it now falls outside the data).
  * The time portion is always the full 00:00-23:59 day (it has no data-derived bounds). Clearing a time
    field (--:--) widens that end to the whole day: start-of-day for the range start, end-of-day for the end.

Run with:  hatch run example
"""

import datetime as dt

import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


def load_timeseries(start_offset_days: int = 0, num_days: int = 30) -> pd.DataFrame:
    """Fake dynamic data: one row per day, each with a non-midnight time-of-day.

    The time component matters: a datetime column whose values are all at midnight is typed as "date"
    (and would default to `DatePicker`), whereas the varied times below make it a genuine "datetime"
    column so `DateTimePicker` is allowed. Both arguments are driven from the dashboard so the date
    range shifts/extends at runtime, letting you watch the dynamic pickers' bounds update.
    """
    base = dt.datetime(2024, 1, 1) + dt.timedelta(days=start_offset_days)
    rows = [
        {
            # Spread the time-of-day across rows so the column is "datetime", not "date".
            "timestamp": base + dt.timedelta(days=i, hours=(i * 5) % 24, minutes=(i * 13) % 60),
            "value": (i * 7) % 50,
            "category": ["A", "B", "C"][i % 3],
        }
        for i in range(num_days)
    ]
    return pd.DataFrame(rows)


# Register as DYNAMIC data (a function referenced by name) so the filters become dynamic.
data_manager["timeseries"] = load_timeseries


page = vm.Page(
    title="Dynamic DateTimePicker",
    components=[
        vm.Graph(
            id="ts_graph",
            figure=px.scatter("timeseries", x="timestamp", y="value", color="category"),
        ),
    ],
    controls=[
        # --- The two selectors under test ---------------------------------------------------------
        # Range ("multi") DateTimePicker: a From and a To date+time pair (range=True is the default).
        vm.Filter(column="timestamp", selector=vm.DateTimePicker(title="Range DateTimePicker (multi)")),
        # Single DateTimePicker: one date+time.
        vm.Filter(column="timestamp", selector=vm.DateTimePicker(range=False, title="Single DateTimePicker")),
        # --- Drive the dynamic data_frame at runtime (data_frame parameters) ----------------------
        vm.Parameter(
            targets=["ts_graph.data_frame.start_offset_days"],
            selector=vm.Slider(min=0, max=60, step=5, value=0, title="Start offset (days) — moves min"),
        ),
        vm.Parameter(
            targets=["ts_graph.data_frame.num_days"],
            selector=vm.Slider(min=5, max=90, step=5, value=30, title="Number of days — moves max"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
