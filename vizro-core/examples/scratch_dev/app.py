"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card

from data import superstore_df
from charts import (
    bar_chart_by_subcategory,
    bar_chart_by_category,
    bar_chart_sales_by_customer,
    custom_aggrid,
    create_map_bubble_new,
    create_bar_chart_by_region,
    create_product_performance_chart,
    create_line_chart_per_month,
    create_bar_current_vs_previous_segment,
)

df = px.data.iris()

vm.Page.add_type("controls", vm.Button)

page_0 = vm.Page(
    title="Overview dashboard",
    components=[
        vm.Container(
            title="",
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
                        value_format="${value:0.2f}",
                        icon="money_bag",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=superstore_df,
                        value_column="Order ID",
                        title="Orders",
                        value_format="{value:,}",
                        icon="numbers",
                        agg_func="nunique",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=superstore_df,
                        value_column="Customer ID",
                        title="Customers",
                        value_format="{value:,}",
                        icon="numbers",
                        agg_func="nunique",
                    )
                ),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3]]),
        ),
        vm.Container(
            title="Regional view",
            components=[
                vm.Graph(id="region_map_chart", figure=create_map_bubble_new(superstore_df, value_col="Sales")),
                vm.Graph(id="region_bar_chart", figure=create_bar_chart_by_region(superstore_df, value_col="Sales")),
            ],
            layout=vm.Grid(grid=[[0, 1]]),
            variant="filled",
        ),
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    id="bar_chart_by_segment",
                    figure=create_bar_current_vs_previous_segment(superstore_df, value_col="Sales"),
                ),
            ],
            variant="filled",
        ),
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    id="line_chart_by_month",
                    figure=create_line_chart_per_month(
                        superstore_df,
                        value_col="Sales",
                    ),
                ),
                vm.Graph(id="customer_bar_chart", figure=bar_chart_sales_by_customer(superstore_df, value_col="Sales")),
            ],
            layout=vm.Grid(grid=[[0, 0, 1]]),
            variant="filled",
        ),
    ],
    controls=[
        vm.Parameter(
            selector=vm.RadioItems(options=["Sales", "Profit"], title="Metric"),
            targets=[
                "region_map_chart.value_col",
                "region_bar_chart.value_col",
                "customer_bar_chart.value_col",
                "line_chart_by_month.value_col",
                "bar_chart_by_segment.value_col",
            ],
        )
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 2, 2],
            [1, 1, 1, 1, 2, 2],
            [3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3],
        ],
        row_gap="12px",
    ),
)

page_1 = vm.Page(
    title="Table",
    components=[vm.AgGrid(id="table_id", figure=custom_aggrid(superstore_df))],
    controls=[
        vm.Filter(
            column="Order Date",
            selector=vm.DatePicker(
                range=True,
            ),
        ),
        vm.Button(
            text="Export data",
            icon="download",
            actions=[va.export_data(targets=["table_id"], file_format="xlsx")],
            # description="Download data",
            variant="outlined",
        ),
        vm.Button(
            text="",
            icon="Reset Settings",
            description="Reset actions",
            variant="outlined",
        ),
    ],
)

page_2 = vm.Page(
    title="Detailed view",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Graph(figure=create_product_performance_chart(superstore_df)),
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Sales",
                            components=[
                                vm.Graph(
                                    figure=bar_chart_by_category(
                                        superstore_df, value_col="Sales", custom_data=["Category"]
                                    ),
                                    actions=va.filter_interaction(),
                                ),
                                vm.Graph(
                                    figure=bar_chart_by_subcategory(
                                        superstore_df,
                                        value_col="Sales",
                                        custom_data=["Sub-Category"],
                                    ),
                                    actions=va.filter_interaction(),
                                ),
                            ],
                            # variant="filled",
                        ),
                        vm.Container(
                            title="Profit",
                            components=[
                                vm.Graph(
                                    figure=bar_chart_by_category(
                                        superstore_df, value_col="Profit", custom_data=["Category"]
                                    ),
                                    actions=va.filter_interaction(),
                                ),
                                vm.Graph(
                                    figure=bar_chart_by_subcategory(
                                        superstore_df,
                                        value_col="Profit",
                                        custom_data=["Sub-Category"],
                                    ),
                                    actions=va.filter_interaction(),
                                ),
                            ],
                            # variant="filled",
                        ),
                    ]
                ),
            ],
            layout=vm.Grid(
                grid=[
                    [0, 0, 1],
                    [0, 0, 1],
                ]
            ),
        )
    ],
    controls=[
        vm.Button(
            text="",
            icon="Reset Settings",
            description="Reset actions",
            variant="outlined",
        )
    ],
)


navigation = vm.Navigation(
    pages=["Overview dashboard", "Table", "Detailed view"],
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(pages=["Overview dashboard", "Detailed view"], label="Dashboard", icon="analytics"),
            vm.NavLink(
                pages=["Table"],
                icon="table",
                label="Table",
            ),
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_0, page_1, page_2], navigation=navigation)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
