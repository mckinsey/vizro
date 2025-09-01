"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture
from vizro.figures import kpi_card
import time
import pandas as pd
from data import summary, industry_data, industry_verticals
from charts import custom_bar

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})

vm.Page.add_type("components", vm.Slider)
vm.Container.add_type("components", vm.Slider)

page_1 = vm.Page(
    title="Page 1",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Slider(
                    id="slider-component-1",
                    marks={0: "page 1", 1: "page 2", 2: "page 3"},
                    step=1,
                    min=0,
                    max=2,
                    extra={"included": True}
                )
            ]
        ),
        vm.Figure(
            id="kpi-card-1",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Number of Leads",
                    icon="Groups",
                ),
        ),
        vm.Figure(
            id="kpi-card-2",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Serviceable Available Market",
                    icon="Finance mode",
                ),
        ),
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    figure=custom_bar(industry_data)
                )
            ]
        ),
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text")
            ]
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0],
            [1, 1, 2, 2],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
        ],
        row_gap="8px",
    )
)

page_2 = vm.Page(
    title="Page 2",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Slider(
                    id="slider-component-2",
                    marks={0: "page 1", 1: "page 2", 2: "page 3"},
                    step=1,
                    min=0,
                    max=2,
                    extra={"included": True}
                )
            ]
        ),
        vm.Figure(
            id="kpi-card-3",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Number of Leads",
                    icon="Groups",
                ),
        ),
        vm.Figure(
            id="kpi-card-4",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Serviceable Available Market",
                    icon="Finance mode",
                ),
        ),
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
            ]
        ),
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text")
            ]
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0],
            [1, 1, 2, 2],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
        ],
        row_gap="8px",
    )
)

page_3 = vm.Page(
    title="Page 3",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Slider(
                    id="slider-component-3",
                    marks={0: "page 1", 1: "page 2", 2: "page 3"},
                    step=1,
                    min=0,
                    max=2,
                    extra={"included": True}
                )
            ]
        ),
        vm.Figure(
            id="kpi-card-5",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Number of Leads",
                    icon="Groups",
                ),
        ),
        vm.Figure(
            id="kpi-card-6",
            figure=kpi_card(
                    data_frame=df_kpi,
                    value_column="Actual",
                    title="Serviceable Available Market",
                    icon="Finance mode",
                ),
        ),
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
            ]
        ),
        vm.Container(
            title="",
            components=[
                vm.Card(text="Placeholder text"),
                vm.Card(text="Placeholder text")
            ]
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0],
            [1, 1, 2, 2],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
            [3, 3, 4, 4],
        ],
        row_gap="8px",
    )
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
