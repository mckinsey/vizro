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
        vm.RadioItems(
            id="radio_items_id",
            options=["Both shifts", "First shift", "Second shift"],
            value="Both shifts",
            actions=vm.Action(
                function=update_time_pickers("radio_items_id"),
                outputs=["time_picker_id-start.value", "time_picker_id-end.value"],
            )
        ),
        vm.Filter(
            visible=False,
            column="datetime_utc",
            selector=vm.TimePicker(
                id="time_picker_id",
                range=True,
                extra=dict(
                    withDropdown=True,
                    presets=[
                        {"label": '08am -> 08pm (first shift)', "values": ['08:00:00']},
                        {"label": '08pm -> 08am (second shift)', "values": ['20:00:00']},
                    ],
                )
            ),
        ),

    ]

)

dashboard = vm.Dashboard(
    pages=[
        page_0,
        page_1,
        page_2,
        page_3,
        page_4,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
