"""Example to show dashboard configuration."""

import datetime
import random

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

date_data_frame = pd.DataFrame(
    {
        "type": [random.choice(["A", "B", "C"]) for _ in range(31)],
        "value": [random.randint(0, 100) for _ in range(31)],
        "time": [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)],
    }
)

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(figure=px.line(date_data_frame, x="time", y="value")),
    ],
    controls=[
        vm.Filter(column="type"),
        vm.Filter(column="value"),
        vm.Filter(column="time"),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
