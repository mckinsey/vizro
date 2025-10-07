"""Dev app to try things out."""

import json
import base64

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

from data import superstore_df, create_superstore_product, pareto_customers_table
from charts import (
    bar_chart_by_subcategory,
    bar_chart_by_category,
    bar_chart_by_customer,
    custom_aggrid,
    create_map_bubble_new,
    create_bar_chart_by_region,
    create_line_chart_per_month,
    create_bar_current_vs_previous_segment,
    pareto_customers_chart,
    scatter_with_quadrants,
    pie_chart_by_category,
)
from charts import COLUMN_DEFS_PRODUCT, COLUMN_DEFS_CUSTOMERS

df = px.data.iris()

vm.Page.add_type("controls", vm.Button)
vm.Container.add_type("controls", vm.Button)

superstore_product_df = create_superstore_product(superstore_df)
aggrid_df = pareto_customers_table(superstore_df)
state_list = superstore_df["State_Code"].unique().tolist()
categories = superstore_df["Category"].unique().tolist()
subcategories = superstore_df["Sub-Category"].unique().tolist()
customer_name = superstore_df["Customer Name"].unique().tolist()
customer_name.append("NONE")


def _encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


@capture("action")
def nav_region(parameter_value):
    url_query_params = f"?pg2-parameter-2={_encode_to_base64(parameter_value)}"
    return "/regional-view", url_query_params


@capture("action")
def nav_product(parameter_value):
    return "/product-view"


@capture("action")
def nav_customer(parameter_value):
    return "/customer-view"


page_1 = vm.Page(
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
                    actions=vm.Action(
                        function=nav_region("pg1_parameter_1"), outputs=["vizro_url.pathname", "vizro_url.search"]
                    ),
                ),
            ],
            layout=vm.Grid(grid=[*[[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]] * 5, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]]),
            variant="filled",
        ),
        vm.Container(
            title="Current vs Previous Year by Customer Segment",
            components=[
                vm.Graph(
                    id="bar_chart_by_segment",
                    figure=create_bar_current_vs_previous_segment(superstore_df, value_col="Sales"),
                ),
                vm.Button(
                    id="segment-nav-btn",
                    text="",
                    icon="jump_to_element",
                    variant="outlined",
                    description="Click to access detailed customer view",
                    actions=vm.Action(
                        function=nav_customer("pg1_parameter_1"), outputs=["vizro_url.pathname", "vizro_url.search"]
                    ),
                ),
            ],
            variant="filled",
            layout=vm.Grid(grid=[*[[-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]] * 5, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1]]),
        ),
        vm.Container(
            title="",
            layout=vm.Grid(grid=[[0], [0], [0], [0], [0],[1]]),
            components=[
                vm.Graph(
                    id="line_chart_by_month",
                    figure=create_line_chart_per_month(
                        superstore_df,
                        value_col="Sales",
                    ),
                ),
                vm.Button(
                    id="customer-nav-btn",
                    text="",
                    icon="jump_to_element",
                    variant="outlined",
                    description="Click to access detailed customer view",
                    actions=vm.Action(
                        function=nav_product("pg1_parameter_1"), outputs=["vizro_url.pathname", "vizro_url.search"]
                    ),
                ),
            ],
            variant="filled",
        ),
        vm.Container(
            title="",
            components=[
                vm.Graph(id="customer_pie_chart", figure=pie_chart_by_category(superstore_df, value_col="Sales")),
            ],
            variant="filled",
        ),
    ],
    controls=[
        vm.Parameter(
            id="pg1_parameter_1",
            selector=vm.RadioItems(options=["Sales", "Profit", "Order ID", "Customer ID"], title="Metric"),
            targets=[
                "region_bar_chart.value_col",
                "customer_pie_chart.value_col",
                "line_chart_by_month.value_col",
                "bar_chart_by_segment.value_col",
            ],
            show_in_url=True,
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 0, 0],
            [1, 1, 1, 2, 2],
            [1, 1, 1, 2, 2],
            [1, 1, 1, 2, 2],
            [3, 3, 3, 4, 4],
            [3, 3, 3, 4, 4],
            [3, 3, 3, 4, 4],
        ],
    ),
)

page_2 = vm.Page(
    title="Regional view",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    id="region_map_chart",
                    figure=create_map_bubble_new(superstore_df, value_col="Sales", custom_data=["State_Code"]),
                    actions=[
                        va.set_control(control="pg2-filter-1", value="State_Code"),
                    ],
                ),
            ],
        ),
        vm.Container(
            components=[
                vm.Graph(
                    id="regional_category",
                    figure=bar_chart_by_category(superstore_df, value_col="Sales", custom_data=["Category"]),
                    actions=[
                        va.set_control(control="pg2-filter-2", value="Category"),
                        va.set_control(control="pg2-parameter-1", value="Category"),
                    ],
                ),
                vm.Graph(
                    id="regional_subcategory",
                    figure=bar_chart_by_subcategory(
                        superstore_df,
                        value_col="Sales",
                        custom_data=["Sub-Category"],
                    ),
                    actions=[
                        va.set_control(control="pg2-filter-3", value="Sub-Category"),
                    ],
                ),
                vm.Graph(id="customer_bar_chart_2", figure=bar_chart_by_customer(superstore_df, value_col="Sales")),
            ],
            variant="filled",
            layout=vm.Grid(grid=[[0], [1], [2]]),
        ),
    ],
    controls=[
        vm.Filter(
            id="pg2-filter-1",
            column="State_Code",
            selector=vm.Dropdown(),
        ),
        vm.Filter(
            id="pg2-filter-2",
            column="Category",
            selector=vm.Dropdown(),
            targets=["regional_subcategory", "customer_bar_chart_2", "region_map_chart"],
        ),
        vm.Parameter(
            id="pg2-parameter-1",
            targets=["regional_category.highlight_category"],
            selector=vm.Dropdown(
                multi=False, options=["Furniture", "Technology", "Office Supplies", "NONE"], value="NONE"
            ),
        ),
        vm.Filter(id="pg2-filter-3", column="Sub-Category", selector=vm.Dropdown(), targets=["customer_bar_chart_2"]),
        vm.Parameter(
            id="pg2-parameter-2",
            targets=[
                "regional_subcategory.value_col",
                "customer_bar_chart_2.value_col",
                "region_map_chart.value_col",
                "regional_category.value_col",
            ],
            selector=vm.RadioItems(options=["Sales", "Profit", "Order ID"], title="Metric"),
            show_in_url=True,
        ),
        vm.Button(
            text="",
            icon="Reset Settings",
            description="Reset actions",
            variant="outlined",
            actions=[
                vm.Action(
                    function=capture("action")(lambda: [state_list, categories, "NONE", subcategories])(),
                    outputs=["pg2-filter-1", "pg2-filter-2", "pg2-parameter-1", "pg2-filter-3"],
                )
            ],
        ),
    ],
    layout=vm.Grid(grid=[[0, 0, 0, 1, 1]]),
)

page_3 = vm.Page(
    title="Customer view",
    components=[
        vm.Graph(
            id="pg3_pareto_chart", figure=pareto_customers_chart(superstore_df.head(30), custom_data=["Customer Name"])
        ),
        vm.AgGrid(
            id="table-2",
            figure=dash_ag_grid(
                aggrid_df.head(30),
                columnDefs=COLUMN_DEFS_CUSTOMERS,
            ),
            actions=va.set_control(control="pg3_parameter_1", value="Customer Name"),
        ),
    ],
    controls=[
        vm.Filter(id="pg3_filter_1", column="Order Date", selector=vm.DatePicker(range=True)),
        vm.Parameter(
            id="pg3_parameter_1",
            targets=["pg3_pareto_chart.highlight_customer"],
            selector=vm.Dropdown(options=customer_name, value="NONE", multi=False),
        ),
    ],
    layout=vm.Grid(grid=[[0, 0, 1, 1]]),
)


page_4 = vm.Page(
    title="Product view",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Graph(
                    id="scatter",
                    figure=scatter_with_quadrants(
                        data_frame=superstore_product_df, x="Sales", y="Profit", custom_data=["Product Name"]
                    ),
                ),
                vm.AgGrid(id="table", figure=dash_ag_grid(superstore_product_df, columnDefs=COLUMN_DEFS_PRODUCT)),
            ],
            layout=vm.Grid(grid=[[0, 0, 0, 1, 1]]),
        ),
    ],
    controls=[
        vm.Filter(column="Category / Sub-Category", selector=vm.Dropdown(multi=False, value="Technology / Phones")),
    ],
)

page_5 = vm.Page(
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


navigation = vm.Navigation(
    pages=["Overview dashboard", "Regional view", "Customer view", "Product view", "Table"],
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(
                pages=["Overview dashboard"],
                label="Overview",
                icon="Home",
            ),
            vm.NavLink(
                pages=["Regional view"],
                label="Region",
                icon="Globe Asia",
            ),
            vm.NavLink(
                pages=["Product view"],
                label="Product",
                icon="Barcode",
            ),
            vm.NavLink(
                pages=["Table"],
                icon="Shopping Cart",
                label="Orders",
            ),
            vm.NavLink(
                pages=["Customer view"],
                label="Customer",
                icon="Group",
            ),
        ]
    ),
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5], navigation=navigation, theme="vizro_light")


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
