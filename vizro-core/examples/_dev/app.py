"""Example to show dashboard configuration."""

import datetime

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_ag_grid, dash_data_table

# Sample DataFrame with mixed date types
df = pd.DataFrame(
    {
        "year": [
            "1-1-1952",
            "1/1/1952",
            "1952-1-1",
            "1952-01-01",
            "1952-01-01 20:20:20",
            datetime.datetime(1952, 1, 1),
            datetime.datetime(1952, 1, 1, 20, 20, 20),
            datetime.date(1952, 1, 1),
            datetime.date(1952, 1, 1).isoformat(),
        ],
    }
)

# df["year"] = pd.to_datetime(df["year"], format="mixed")

gapminder_df = px.data.gapminder()
gapminder_df["year"] = pd.to_datetime(gapminder_df["year"], format="%Y")


vm.Page.add_type("components", vm.DatePicker)

page_date = vm.Page(
    title="AG Grid Default",
    layout=vm.Layout(grid=[[0, 1], [2, 3], [4, 5]]),
    components=[
        vm.Table(
            id="table_1",
            figure=dash_data_table(data_frame=df),
            actions=[
                vm.Action(
                    function=filter_interaction(
                        targets=[
                            # "table_1",
                            "table_2",
                            "ag_grid",
                            "graph",
                        ]
                    )
                )
            ],
        ),
        vm.AgGrid(
            id="ag_grid",
            figure=dash_ag_grid(data_frame=df, dashGridOptions={"pagination": False}),
        ),
        vm.Table(
            id="table_2",
            figure=dash_data_table(data_frame=df),
        ),
        vm.Graph(
            id="graph",
            figure=px.line(
                gapminder_df,
                x="year",
                y="gdpPercap",
                color="continent",
                custom_data=["year"],
            ),
        ),
        vm.Button(text="Export", actions=[vm.Action(function=export_data())]),
        vm.DatePicker(),
    ],
    controls=[
        vm.Filter(column="year"),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker()
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=True
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False
        #     )
        # ),
        #
        #
        #
        #
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         value="1952-01-01"
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         value=["1952-01-01"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         value=["1952-01-01", "1952-01-02"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         value=["1952-01-01", "1952-01-02", "1952-01-03"]
        #     )
        # ),
        #
        #
        #
        #
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=True,
        #         value="1952-01-01",
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=True,
        #         value=["1952-01-01"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=True,
        #         value=["1952-01-01", "1952-01-02"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=True,
        #         value=["1952-01-01", "1952-01-02", "1952-01-03"]
        #     )
        # ),
        #
        #
        #
        #
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value="1952-01-01",
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value=["1952-01-01"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value=["1952-01-01", "1952-01-02"]
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value=["1952-01-01", "1952-01-02", "1952-01-03"]
        #     )
        # ),
        #
        #
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value="1952-01-01",
        #         min="1952-01-01",
        #         max="1952-01-02",
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value="1952-01-01",
        #         min="1952-01-02",
        #         max="1952-01-01",
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value="1952-01-01",
        #         min="1952-01-01",
        #         max="1952-01-01",
        #     )
        # ),
        # vm.Filter(
        #     column="year",
        #     selector=vm.DatePicker(
        #         range=False,
        #         value="1952-01-01",
        #         min="1952-01-02",
        #         max="1952-01-02",
        #     )
        # ),
    ],
)

page_2 = vm.Page(title="page2", components=[vm.Button()])

dashboard = vm.Dashboard(pages=[page_date, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
