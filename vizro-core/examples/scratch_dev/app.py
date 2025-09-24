"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card

from data import superstore_df
from charts import (
    create_map_bubble,
    bar_chart_by_segment,
    bar_chart_by_product,
    bar_chart_by_subcategory,
    bar_chart_by_category,
    bar_chart_sales_by_customer,
    custom_aggrid,
)

df = px.data.iris()


page_1 = vm.Page(
    title="Overview Dashboard",
    components=[
        vm.Tabs(
            tabs=[
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
                                value_format="${value:0.2f}",
                                icon="money_bag",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=superstore_df,
                                value_column="Order ID",
                                title="No. Orders",
                                value_format="{value:,}",
                                icon="numbers",
                                agg_func="nunique",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=superstore_df,
                                value_column="Customer ID",
                                title="No. Customers",
                                value_format="{value:,}",
                                icon="numbers",
                                agg_func="nunique",
                            )
                        ),
                        vm.Graph(figure=create_map_bubble(superstore_df, value_col="Sales")),
                        vm.Graph(
                            figure=bar_chart_by_segment(superstore_df, value_col="Sales", custom_data=["Segment"]),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_by_product(superstore_df, value_col="Sales", custom_data=["Product Name"]),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_by_category(superstore_df, value_col="Sales", custom_data=["Category"]),
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
                            figure=bar_chart_sales_by_customer(
                                superstore_df, value_col="Sales", custom_data=["Customer Name"]
                            ),
                            actions=va.filter_interaction(),
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 0, 4, 4, 4, 5, 5, 5, 6, 6, 6],
                            [1, 1, 4, 4, 4, 5, 5, 5, 6, 6, 6],
                            [2, 2, 7, 7, 7, 8, 8, 8, 9, 9, 9],
                            [3, 3, 7, 7, 7, 8, 8, 8, 9, 9, 9],
                        ],
                        row_min_height="150px",
                    ),
                ),
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
                                value_format="${value:0.2f}",
                                icon="money_bag",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=superstore_df,
                                value_column="Order ID",
                                title="No. Orders",
                                value_format="{value:,}",
                                icon="numbers",
                                agg_func="nunique",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=superstore_df,
                                value_column="Customer ID",
                                title="No. Customers",
                                value_format="{value:,}",
                                icon="numbers",
                                agg_func="nunique",
                            )
                        ),
                        vm.Graph(figure=create_map_bubble(superstore_df, value_col="Profit")),
                        vm.Graph(
                            figure=bar_chart_by_segment(superstore_df, value_col="Profit", custom_data=["Segment"]),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_by_product(
                                superstore_df,
                                value_col="Profit",
                                custom_data=["Product Name"],
                            ),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_by_category(superstore_df, value_col="Profit", custom_data=["Category"]),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_by_subcategory(
                                superstore_df, value_col="Profit", custom_data=["Sub-Category"]
                            ),
                            actions=va.filter_interaction(),
                        ),
                        vm.Graph(
                            figure=bar_chart_sales_by_customer(
                                superstore_df, value_col="Profit", custom_data=["Customer Name"]
                            ),
                            actions=va.filter_interaction(),
                        ),
                    ],
                    layout=vm.Grid(
                        grid=[
                            [0, 0, 4, 4, 4, 5, 5, 5, 6, 6, 6],
                            [1, 1, 4, 4, 4, 5, 5, 5, 6, 6, 6],
                            [2, 2, 7, 7, 7, 8, 8, 8, 9, 9, 9],
                            [3, 3, 7, 7, 7, 8, 8, 8, 9, 9, 9],
                        ],
                        row_min_height="150px",
                    ),
                ),
            ]
        ),
    ],
    controls=[
        vm.Filter(
            column="Order Date",
            selector=vm.DatePicker(
                range=True,
            ),
        ),
    ],
)

page_2 = vm.Page(title="Table", components=[vm.AgGrid(figure=custom_aggrid(superstore_df))])

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
