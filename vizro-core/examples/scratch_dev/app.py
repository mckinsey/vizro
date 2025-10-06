"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

from data import superstore_df, create_superstore_product
from charts import (
    bar_chart_by_subcategory,
    bar_chart_by_category,
    bar_chart_by_customer,
    custom_aggrid,
    create_map_bubble_new,
    create_bar_chart_by_region,
    create_line_chart_per_month,
    create_line_chart_sales_per_month,
    create_bar_current_vs_previous_segment,
    pareto_customers_chart,
    scatter_with_quadrants,
    treemap_chart,
    pie_chart_by_category,
    pie_chart_by_segment
)
from charts import COLUMN_DEFS_PRODUCT

df = px.data.iris()

vm.Page.add_type("controls", vm.Button)
vm.Container.add_type("controls", vm.Button)

superstore_product_df = create_superstore_product(superstore_df)


@capture("action")
def nav_action():
    pass


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
                vm.Graph(id="region_bar_chart", figure=create_bar_chart_by_region(superstore_df, value_col="Sales")),
                vm.Button(
                    id="region-nav-btn",
                    text="",
                    icon="jump_to_element",
                    variant="outlined",
                    description="Click to access detailed regional view",
                )
            ],
            layout=vm.Grid(
                grid=[
                    *[[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]] * 5,
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
                ]
            ),
            variant="filled",
        ),
        vm.Container(
            title="Current vs Previous Year by Segment",
            components=[
                vm.Graph(
                    id="bar_chart_by_segment",
                    figure=create_bar_current_vs_previous_segment(superstore_df, value_col="Sales"),
                    # title="Current vs Previous Year by Segment",
                ),
                vm.Button(
                    id="segment-nav-btn",
                    text="",
                    icon="jump_to_element",
                    variant="outlined",
                    description="Click to access detailed customer view",
                )
            ],
            variant="filled",
            layout=vm.Grid(
                grid=[
                    *[[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]] * 5,
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]
                ]
            ),
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
                vm.Graph(id="customer_pie_chart", figure=pie_chart_by_category(superstore_df, value_col="Sales")),
                vm.Button(
                    id="customer-nav-btn",
                    text="",
                    icon="jump_to_element",
                    variant="outlined",
                    description="Click to access detailed customer view",
                )
            ],
            layout=vm.Grid(
                grid=[
                    *[[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]] * 5,
                    [ 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                ],
                col_gap="2px"
            ),
            variant="filled",
        ),
    ],
    controls=[
        vm.Parameter(
            selector=vm.RadioItems(options=["Sales", "Profit", "Order ID"], title="Metric"),
            targets=[
                "region_bar_chart.value_col",
                "customer_pie_chart.value_col",
                "line_chart_by_month.value_col",
                "bar_chart_by_segment.value_col",
            ],
        ),
        vm.Parameter(
            id="highlight_region_parameter",
            targets=["region_bar_chart.highlight_region"],
            selector=vm.Dropdown(multi=False, options=["Central", "East", "West", "South", "NONE"], value="NONE"),
        ),
        vm.Button(
            text="",
            icon="Reset Settings",
            description="Reset actions",
            variant="outlined",
            actions=[
                vm.Action(
                    function=capture("action")(
                        lambda: ["NONE", "NONE"]
                    )(),
                    outputs=["highlight_region_parameter"],
                )
            ]
        ),
        vm.Filter(
            id="filter_region",
            column="Region",
            selector=vm.Dropdown(),
            # targets=["customer_bar_chart", "line_chart_by_month", "bar_chart_by_segment"]
        )
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3, 3],
            [3, 3, 3, 3, 3, 3, 3],
        ],
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

page_3 = vm.Page(
    title="Customer view",
    components=[
        vm.Graph(
            figure=pareto_customers_chart(superstore_df)
        ),
        vm.Graph(figure=pie_chart_by_segment(superstore_df, value_col="Sales", custom_data=["Segment"])),
        vm.Graph(id="customer_bar_chart", figure=bar_chart_by_customer(superstore_df, value_col="Sales")),
    ],
    controls=[
        vm.Filter(
            column="Segment", selector=vm.Dropdown()
        )
    ],
    layout=vm.Grid(grid=[
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 2, 2],
        [0, 0, 0, 2, 2],
        [0, 0, 0, 2, 2]
    ]
    )
)

page_4 = vm.Page(
    title="Regional view",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    id="region_map_chart",
                    figure=create_map_bubble_new(superstore_df, value_col="Sales", custom_data=["Region"]),
                ),
            ],
        ),
        vm.Container(
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
                vm.Graph(
                    id="customer_bar_chart_2",
                    figure=bar_chart_by_customer(superstore_df, value_col="Sales")
                ),
            ],
            variant="filled",
            layout=vm.Grid(grid=[[0], [1], [2]])
        ),
    ],
    controls=[
        vm.Filter(
            column="Region",
            selector=vm.Dropdown(),
        )
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 0, 1, 1],
        ]
    )
)

page_5 = vm.Page(
    title="Product view",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Product overview",
                    components=[
                        vm.Graph(
                            figure=treemap_chart(
                                superstore_df,
                                path=["Segment", "Category", "Sub-Category"],
                                values="Sales",
                                color="Profit",
                                title="Sales and Profit Treemap by Segment > Category > Sub-Category"
                            )
                        ),
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
                    layout=vm.Grid(grid=[
                        [0, 0, 0, 1, 1],
                        [0, 0, 0, 2, 2],
                    ])
                ),
                vm.Container(
                    title="Detailed view",
                    components=[
                        vm.Graph(id="scatter",
                                 figure=scatter_with_quadrants(data_frame=superstore_product_df, x="Sales", y="Profit",
                                                               custom_data=["Product Name"])),
                        vm.AgGrid(id="table",
                                  figure=dash_ag_grid(superstore_product_df, columnDefs=COLUMN_DEFS_PRODUCT)),
                    ],
                    controls=[
                        vm.Filter(column="Category / Sub-Category",
                                  selector=vm.Dropdown(multi=False, value="Technology / Phones")),
                    ],
                    layout=vm.Grid(grid=[[0, 0, 0, 1, 1]])
                ),
            ]
        ),

    ],
)


navigation = vm.Navigation(
    pages=["Overview dashboard", "Table", "Customer view", "Regional view", "Product view"],
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(
                pages=["Overview dashboard", "Customer view", "Regional view", "Product view"],
                label="Dashboard",
                icon="analytics"
            ),
            vm.NavLink(
                pages=["Table"],
                icon="table",
                label="Table",
            ),
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_0, page_1, page_3, page_4, page_5], navigation=navigation)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
