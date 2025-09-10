"""Dev app to try things out."""

import pandas as pd

from dash import ctx
from dash.exceptions import PreventUpdate
import time

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture
from vizro.tables import dash_ag_grid
from vizro.figures import kpi_card
from vizro.managers import data_manager
from charts import create_bubble

df = px.data.iris()
from data import superstore_df


page_1 = vm.Page(
    title="Overview Dashboard",
    components=[
        vm.Container(
            components=[
                vm.Container(
                    title="Controls",
                    components=[vm.Card(text="Placeholder text")],
                    collapsed=True,
                ),
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Profit",
                            components=[
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Sales",
                                        title="Sales",
                                        value_format="${value:0.2f}",
                                        icon="bar_chart",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Profit",
                                        title="Profit",
                                        value_format="${value:,}",
                                        icon="money_bag",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Row ID",
                                        title="No. Orders",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Customer ID",
                                        title="No. Customers",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Graph(figure=create_bubble(superstore_df)),
                                vm.Card(text="Placeholder bar chart by segment"),
                                vm.Card(text="Placeholder bar chart top 10 manufacturers"),
                                vm.Card(text="Placeholder bar chart sales by category"),
                                vm.Card(text="Placeholder bar chart by sub-category"),
                                vm.Card(text="Placeholder bar chart top 10 customers"),
                            ],
                            layout=vm.Grid(
                                grid=[
                                    [0, 1, 2, 3],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                ],
                                row_min_height="150px",
                            ),
                        ),
                        vm.Container(
                            title="Sales",
                            components=[
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Sales",
                                        title="Sales",
                                        value_format="${value:0.2f}",
                                        icon="bar_chart",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Profit",
                                        title="Profit",
                                        value_format="${value:,}",
                                        icon="money_bag",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Row ID",
                                        title="No. Orders",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Customer ID",
                                        title="No. Customers",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Graph(figure=create_bubble(superstore_df)),
                                vm.Card(text="Placeholder bar chart by segment"),
                                vm.Card(text="Placeholder bar chart top 10 manufacturers"),
                                vm.Card(text="Placeholder bar chart sales by category"),
                                vm.Card(text="Placeholder bar chart by sub-category"),
                                vm.Card(text="Placeholder bar chart top 10 customers"),
                            ],
                            layout=vm.Grid(
                                grid=[
                                    [0, 1, 2, 3],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                ],
                                row_min_height="150px",
                            ),
                        ),
                        vm.Container(
                            title="Orders",
                            components=[
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Sales",
                                        title="Sales",
                                        value_format="${value:0.2f}",
                                        icon="bar_chart",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Profit",
                                        title="Profit",
                                        value_format="${value:,}",
                                        icon="money_bag",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Row ID",
                                        title="No. Orders",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Figure(
                                    figure=kpi_card(
                                        data_frame=superstore_df,
                                        value_column="Customer ID",
                                        title="No. Customers",
                                        value_format="{value:,}",
                                        icon="money_bag",
                                        agg_func="count",
                                    )
                                ),
                                vm.Graph(figure=create_bubble(superstore_df)),
                                vm.Card(text="Placeholder bar chart by segment"),
                                vm.Card(text="Placeholder bar chart top 10 manufacturers"),
                                vm.Card(text="Placeholder bar chart sales by category"),
                                vm.Card(text="Placeholder bar chart by sub-category"),
                                vm.Card(text="Placeholder bar chart top 10 customers"),
                            ],
                            layout=vm.Grid(
                                grid=[
                                    [0, 1, 2, 3],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [4, 4, 5, 5],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [6, 6, 7, 7],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                    [8, 8, 9, 9],
                                ],
                                row_min_height="150px",
                            ),
                        ),
                    ]
                ),
            ],
            layout=vm.Flex(),
        )
    ],
)

page_2 = vm.Page(title="Table", components=[vm.AgGrid(figure=dash_ag_grid(superstore_df))])

navigation = vm.Navigation(
    pages=["Overview Dashboard", "Table"],
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(pages=["Overview Dashboard"], label="Overview Dashboard", icon="analytics"),
            vm.NavLink(
                pages=["Table"],
                icon="table",
                label="Table",
            ),
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_1, page_2], navigation=navigation)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
