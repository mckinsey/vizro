"""Dev app to try things out."""

import json
import base64

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

from data import superstore_df, create_superstore_product, pareto_customers_table, create_kpi_data
from charts import (
    bar_chart_by_category,
    create_map_bubble_new,
    create_bar_chart_by_region,
    create_line_chart_per_month,
    create_bar_current_vs_previous_segment,
    create_bar_current_vs_previous_category,
    pareto_customers_chart,
    scatter_with_quadrants_subc,
    pie_chart_by_order_status,
    bar_chart_top_n,
    custom_orders_aggrid,
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
subcategories.append("NONE")
customer_name = superstore_df["Customer Name"].unique().tolist()
customer_name.append("NONE")
product_name = superstore_df["Product Name"].unique().tolist()
product_name.append("NONE")

sales_kpi_df = create_kpi_data(superstore_df, value_col="Sales")
profit_kpi_df = create_kpi_data(superstore_df, value_col="Profit")
order_kpi_df = create_kpi_data(superstore_df, value_col="Order ID")
customer_kpi_df = create_kpi_data(superstore_df, value_col="Customer ID")


def _encode_to_base64(value):
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"


@capture("action")
def nav_region(parameter_value):
    url_query_params = f"?pg2-parameter-2={_encode_to_base64(parameter_value)}"
    return "/regions", url_query_params


@capture("action")
def nav_product():
    return "/products"


@capture("action")
def nav_customer():
    return "/customers"


@capture("action")
def nav_orders():
    return "/orders"


page_1 = vm.Page(
    title="Overview",
    components=[
        vm.Container(
            id="pg1-container-1",
            title="💡 Click on a KPI card to update the charts below.",
            components=[
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=sales_kpi_df,
                        value_column="total_2017",
                        reference_column="total_2016",
                        reference_format="{delta_relative:+.1%} vs. last year (${reference:,.0f})",
                        title="Sales",
                        value_format="${value:,.0f}",
                        icon="bar_chart",
                    ),
                    actions=va.set_control(control="pg1_parameter_1", value="Sales"),
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=profit_kpi_df,
                        value_column="total_2017",
                        reference_column="total_2016",
                        reference_format="{delta_relative:+.1%} vs. last year (${reference:,.0f})",
                        title="Profit",
                        value_format="${value:,.0f}",
                        icon="money_bag",
                    ),
                    actions=va.set_control(control="pg1_parameter_1", value="Profit"),
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=order_kpi_df,
                        value_column="total_2017",
                        reference_column="total_2016",
                        reference_format="{delta_relative:+.1%} vs. last year ({reference:,.0f})",
                        title="Orders",
                        value_format="{value:,.0f}",
                        icon="orders",
                        # agg_func="nunique",
                    ),
                    actions=va.set_control(control="pg1_parameter_1", value="Order ID"),
                ),
                vm.Figure(
                    figure=kpi_card_reference(
                        data_frame=customer_kpi_df,
                        value_column="total_2017",
                        reference_column="total_2016",
                        title="Customers",
                        reference_format="{delta_relative:+.1%} vs. last year ({reference:,.0f})",
                        value_format="{value:,.0f}",
                        icon="group",
                        # agg_func="nunique",
                    ),
                    actions=va.set_control(control="pg1_parameter_1", value="Customer ID"),
                ),
            ],
            layout=vm.Grid(grid=[[0, 1, 2, 3]]),
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
            ],
            variant="filled",
        ),
        vm.Container(
            title="",
            components=[
                vm.Graph(id="order_status_chart", figure=pie_chart_by_order_status(superstore_df, value_col="Sales")),
                vm.Button(
                    id="orders-nav-btn",
                    text="View Deep Dive",
                    icon="jump_to_element",
                    variant="outlined",
                    actions=vm.Action(function=nav_orders(), outputs=["vizro_url.pathname"]),
                ),
            ],
            layout=vm.Grid(grid=[[0], [0], [0], [0], [0], [1]]),
            variant="filled",
        ),
        vm.Container(
            components=[
                vm.Graph(id="region_bar_chart", figure=create_bar_chart_by_region(superstore_df, value_col="Sales")),
                vm.Button(
                    id="region-nav-btn",
                    text="View Deep Dive",
                    icon="jump_to_element",
                    variant="outlined",
                    actions=vm.Action(
                        function=nav_region("pg1_parameter_1"), outputs=["vizro_url.pathname", "vizro_url.search"]
                    ),
                ),
            ],
            layout=vm.Grid(grid=[[0], [0], [0], [0], [0], [1]]),
            variant="filled",
        ),
        vm.Container(
            components=[
                vm.Graph(
                    id="bar_chart_by_segment",
                    figure=create_bar_current_vs_previous_segment(superstore_df, value_col="Sales"),
                ),
                vm.Button(
                    id="segment-nav-btn",
                    text="View Deep Dive",
                    icon="jump_to_element",
                    variant="outlined",
                    actions=vm.Action(function=nav_customer(), outputs=["vizro_url.pathname"]),
                ),
            ],
            variant="filled",
            layout=vm.Grid(grid=[[0], [0], [0], [0], [0], [1]]),
        ),
        vm.Container(
            title="",
            layout=vm.Grid(grid=[[0], [0], [0], [0], [0], [1]]),
            components=[
                vm.Graph(
                    id="category_bar_chart",
                    figure=create_bar_current_vs_previous_category(superstore_df, value_col="Sales"),
                ),
                vm.Button(
                    id="customer-nav-btn",
                    text="View Deep Dive",
                    icon="jump_to_element",
                    variant="outlined",
                    actions=vm.Action(function=nav_product(), outputs=["vizro_url.pathname"]),
                ),
            ],
            variant="filled",
        ),
    ],
    controls=[
        vm.Parameter(
            id="pg1_parameter_1",
            selector=vm.RadioItems(
                options=[
                    {"value": "Sales", "label": "Sales"},
                    {"value": "Profit", "label": "Profit"},
                    {"value": "Order ID", "label": "Orders"},
                    {"value": "Customer ID", "label": "Customers"},
                ],
                title="Metric",
            ),
            targets=[
                "region_bar_chart.value_col",
                "category_bar_chart.value_col",
                "order_status_chart.value_col",
                "line_chart_by_month.value_col",
                "bar_chart_by_segment.value_col",
            ],
            show_in_url=True,
            visible=False,
        ),
    ],
    layout=vm.Grid(
        grid=[
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 2],
            [1, 1, 2],
            [1, 1, 2],
            [1, 1, 2],
            [1, 1, 2],
            [3, 4, 5],
            [3, 4, 5],
            [3, 4, 5],
            [3, 4, 5],
            [3, 4, 5],
        ],
    ),
)

page_2 = vm.Page(
    title="Regions",
    components=[
        vm.Container(
            controls=[
                vm.Filter(
                    id="pg2-filter-1",
                    column="State_Code",
                    selector=vm.Dropdown(),
                    visible=False,
                ),
                vm.Filter(
                    column="Segment",
                    selector=vm.Checklist(title="Choose segment"),
                ),
                vm.Filter(
                    column="Category",
                    selector=vm.Checklist(title="Choose category"),
                ),
                vm.Parameter(
                    id="pg2-parameter-2",
                    selector=vm.RadioItems(
                        options=["Sales", "Profit"],
                        title="Choose metric",
                    ),
                    targets=[
                        "region_map_chart.value_col",
                        "pg2-chart-1.x",
                    ],
                ),
            ],
            layout=vm.Grid(grid=[[0, 1]]),
            components=[
                vm.Container(
                    variant="filled",
                    title="",
                    components=[
                        vm.Graph(
                            id="region_map_chart",
                            header="💡 Click on a state to filter charts on the right.",
                            figure=create_map_bubble_new(superstore_df, value_col="Sales", custom_data=["State_Code"]),
                            actions=[
                                va.set_control(control="pg2-filter-1", value="State_Code"),
                            ],
                        ),
                    ],
                ),
                vm.Container(
                    controls=[
                        vm.Parameter(
                            targets=["pg2-chart-1.top_n"],
                            selector=vm.Slider(min=5, max=30, step=5, value=20, title="Choose top N"),
                        ),
                        vm.Parameter(
                            selector=vm.RadioItems(
                                options=["City", "Customer Name", "Sub-Category"],
                                title="Choose y-axis",
                            ),
                            targets=["pg2-chart-1.y"],
                        ),
                    ],
                    components=[
                        vm.Graph(
                            id="pg2-chart-1",
                            figure=bar_chart_top_n(superstore_df, x="Sales", y="City"),
                        ),
                    ],
                    variant="filled",
                ),
            ],
        ),
    ],
)

page_3 = vm.Page(
    title="Customers",
    components=[
        vm.Container(
            layout=vm.Grid(grid=[[0, 1]]),
            controls=[
                vm.Filter(column="Region", selector=vm.Checklist()),
                vm.Filter(column="Segment", selector=vm.Checklist()),
                vm.Filter(column="Category", selector=vm.Checklist()),
            ],
            components=[
                vm.AgGrid(
                    id="table-2",
                    header="💡 Click on a row to highlight the customer.",
                    figure=dash_ag_grid(
                        aggrid_df,
                        columnDefs=COLUMN_DEFS_CUSTOMERS,
                    ),
                    actions=va.set_control(control="pg3_parameter_1", value="Customer Name"),
                ),
                vm.Graph(id="pg3_pareto_chart", figure=pareto_customers_chart(superstore_df, highlight_customer=None)),
            ],
        ),
    ],
    controls=[
        vm.Parameter(
            id="pg3_parameter_1",
            targets=["pg3_pareto_chart.highlight_customer"],
            selector=vm.Dropdown(options=customer_name, value="NONE", multi=False),
            visible=False,
        ),
    ],
)


page_4 = vm.Page(
    title="Products",
    components=[
        vm.Container(
            title="",
            components=[
                vm.Container(
                    title="",
                    components=[
                        vm.Graph(
                            id="pg4-chart-1",
                            figure=bar_chart_by_category(superstore_df, value_col="Sales", custom_data=["Category"]),
                            actions=[
                                va.set_control(control="pg4-filter-1", value="Category"),
                            ],
                        ),
                    ],
                    variant="filled",
                ),
                vm.Container(
                    title="",
                    components=[
                        vm.AgGrid(
                            id="table",
                            figure=dash_ag_grid(superstore_product_df, columnDefs=COLUMN_DEFS_PRODUCT),
                            actions=va.set_control(control="pg4_parameter_1", value="Sub-Category"),
                        ),
                        vm.Graph(
                            id="pg4-chart-3",
                            figure=scatter_with_quadrants_subc(
                                data_frame=superstore_product_df,
                                x="Sales",
                                y="Profit",
                                custom_data=["Sub-Category"],
                            ),
                        ),
                    ],
                    layout=vm.Grid(grid=[[0, 0, 1, 1, 1]]),
                    variant="filled",
                ),
            ],
            layout=vm.Grid(
                grid=[
                    [0, 0, 0, -1, -1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                ]
            ),
        ),
    ],
    controls=[
        vm.Filter(
            id="pg4-filter-1",
            column="Category",
            targets=["pg4-chart-1"],
            selector=vm.Checklist(title="Product Category"),
            visible=False,
        ),
        # vm.Filter(
        #     column="Category / Sub-Category",
        #     targets=["pg4-chart-3"],
        #     selector=vm.Dropdown(multi=False, value="Technology / Phones"),
        # ),
        vm.Parameter(
            id="pg4_parameter_1",
            targets=["pg4-chart-3.highlight_sub_category"],
            selector=vm.Dropdown(options=subcategories, value="NONE", multi=False),
            visible=False,
        ),
    ],
)

page_5 = vm.Page(
    title="Orders",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(id="table_id", figure=custom_orders_aggrid(superstore_df)),
        vm.Button(
            text="Export data",
            icon="download",
            actions=[va.export_data(targets=["table_id"], file_format="xlsx")],
        ),
    ],
)


navigation = vm.Navigation(
    pages=["Overview", "Regions", "Customers", "Products", "Orders"],
    nav_selector=vm.NavBar(
        items=[
            vm.NavLink(
                pages=["Overview"],
                label="Overview",
                icon="Home",
            ),
            vm.NavLink(
                pages=["Regions"],
                label="Regions",
                icon="Globe Asia",
            ),
            vm.NavLink(
                pages=["Products"],
                label="Products",
                icon="Barcode",
            ),
            vm.NavLink(
                pages=["Customers"],
                label="Customers",
                icon="Group",
            ),
            vm.NavLink(
                pages=["Orders"],
                icon="Shopping Cart",
                label="Orders",
            ),
        ]
    ),
)

dashboard = vm.Dashboard(
    title="Superstore dashboard",
    pages=[page_1, page_2, page_3, page_4, page_5],
    navigation=navigation,
    theme="vizro_light",
)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
