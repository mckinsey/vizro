"""Dev app to try things out."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import vizro.actions as va
from vizro.figures import kpi_card
from vizro.models.types import capture

from data import superstore_df
from charts import (
    create_map_bubble,
    bar_chart_by_segment,
    bar_chart_by_product,
    bar_chart_by_subcategory,
    bar_chart_by_category,
    bar_chart_by_customer,
    custom_aggrid,
)

df = px.data.iris()

vm.Page.add_type("controls", vm.Button)


@capture("graph")
def create_discount_analysis_heatmap(data_frame, fill_missing="zero"):
    # Create discount bins
    df_copy = data_frame.copy()
    df_copy["Discount Bin"] = pd.cut(
        df_copy["Discount"], bins=[0, 0.1, 0.2, 0.3, 0.4, 1.0], labels=["0-10%", "10-20%", "20-30%", "30-40%", "40%+"]
    )

    # Calculate profit margin
    df_copy["Profit Margin"] = df_copy["Profit"] / df_copy["Sales"] * 100

    # Aggregate by category and discount bin
    heatmap_data = (
        df_copy.groupby(["Category", "Discount Bin"], observed=True)
        .agg({"Profit Margin": "mean", "Sales": "sum"})
        .reset_index()
    )

    # Pivot for heatmap
    pivot_data = heatmap_data.pivot(index="Category", columns="Discount Bin", values="Profit Margin")

    # Reindex to ensure all discount bins are present for all categories
    all_bins = ["0-10%", "10-20%", "20-30%", "30-40%", "40%+"]
    pivot_data = pivot_data.reindex(columns=all_bins)

    # Handle missing values
    if fill_missing == "zero":
        pivot_data = pivot_data.fillna(0)
    elif fill_missing == "mean":
        pivot_data = pivot_data.fillna(pivot_data.mean().mean())

    # Create custom text to show 'No Data' for original NaN values
    text_data = pivot_data.copy()
    mask = heatmap_data.pivot(index="Category", columns="Discount Bin", values="Profit Margin").reindex(
        columns=all_bins
    )
    text_display = text_data.applymap(lambda x: f"{x:.1f}" if pd.notna(x) and x != 0 else "No Data")

    # For cells that were filled
    original_mask = mask.isna()
    for i, row in enumerate(pivot_data.index):
        for j, col in enumerate(pivot_data.columns):
            if original_mask.loc[row, col]:
                text_display.loc[row, col] = "No Data"
            else:
                text_display.loc[row, col] = f"{pivot_data.loc[row, col]:.1f}"

    fig = px.imshow(
        pivot_data,
        labels=dict(x="Discount Range", y="Category", color="Avg Profit Margin (%)"),
        x=pivot_data.columns,
        y=pivot_data.index,
        title="Profit Margin Heatmap: Category vs Discount Level",
        text_auto=False,
        aspect="auto",
    )

    fig.update_traces(text=text_display.values, texttemplate="%{text}")

    fig.update_layout(
        height=400,
        coloraxis_colorbar=dict(title="Profit<br>Margin (%)", ticksuffix="%"),
        yaxis_title=None,
    )

    return fig



@capture("graph")
def create_product_performance_chart(data_frame):
    # Aggregate by product
    product_agg = (
        data_frame.groupby(["Product Name", "Category"])
        .agg({"Sales": "sum", "Profit": "sum", "Quantity": "sum", "Discount": "mean"})
        .reset_index()
    )

    # Calculate profit margin
    product_agg["Profit Margin %"] = (product_agg["Profit"] / product_agg["Sales"] * 100).round(2)

    fig = px.scatter(
        product_agg,
        x="Discount",
        y="Profit",
        size="Sales",
        color="Category",
        hover_name="Product Name",
        hover_data={
            "Sales": ":$,.0f",
            "Profit": ":$,.0f",
            "Discount": ":.2%",
            "Quantity": ":,.0f",
            "Profit Margin %": ":.2f",
        },
        title="Discount Impact on Profit & Sales",
        labels={"Discount": "Average Discount Rate", "Profit": "Total Profit", "Category": "Product Category"},
        size_max=60,
        # template='plotly_white'
    )

    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")

    fig.update_layout(
        hovermode="closest",
        showlegend=True,
        legend=dict(
            orientation="h",
            title=None,
        ),
    )

    return fig


@capture("graph")
def create_line_chart_per_month_customer(data_frame, value_col="Sales"):
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])

    # Extract year and month separately
    data_frame["Year"] = data_frame["Order Date"].dt.year
    data_frame["Month"] = data_frame["Order Date"].dt.month

    # Aggregate sales by year & month
    monthly = data_frame.groupby(["Year", "Month"], as_index=False).agg({value_col: "sum"})

    # Split data for 2016 (previous year) and 2017 (current year)
    prev_year = monthly[monthly["Year"] == 2016]
    curr_year = monthly[monthly["Year"] == 2017]

    # Create line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=prev_year["Month"], y=prev_year[value_col], mode="lines+markers", name="Previous Year"))

    fig.add_trace(go.Scatter(x=curr_year["Month"], y=curr_year[value_col], mode="lines+markers", name="Current Year"))

    # Improve layout
    fig.update_layout(
        title=f"{value_col} per Month: Current Year vs Previous Year",
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        ),
        yaxis_title=value_col,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


# @capture("graph")
def create_bar_sales_vs_profit_category(data_frame, value_col="Sales"):
    agg_df = data_frame.groupby("Category", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    melted_df = agg_df.melt(id_vars="Category", value_vars=["Sales", "Profit"], var_name="Metric", value_name="Value")

    # Create bar chart
    fig = px.bar(
        melted_df,
        x="Category",
        y="Value",
        color="Metric",
        barmode="group",
        text_auto=".2s",  # short format labels
        title="Sales and Profit per Category",
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
    )

    return fig


@capture("graph")
def create_bar_sales_vs_profit_segment(data_frame, value_col="Sales"):
    agg_df = data_frame.groupby("Segment", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    # Melt the data so we can plot Sales and Profit side by side
    melted_df = agg_df.melt(id_vars="Segment", value_vars=["Sales", "Profit"], var_name="Metric", value_name="Value")

    # Create bar chart
    fig = px.bar(
        melted_df,
        x="Segment",
        y="Value",
        color="Metric",
        barmode="group",
        text_auto=".2s",  # short format labels
        title="Sales and Profit per Segment",
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
    )

    return fig


# @capture("graph")
# def create_bar_current_vs_previous_segment(data_frame, value_col="Sales"):
#     data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
#     data_frame["Year"] = data_frame["Order Date"].dt.year
#
#     # Aggregate by Segment + Year
#     agg_df = data_frame.groupby(["Segment", "Year"], as_index=False).agg({value_col: "sum"})
#
#     # Pivot to get separate columns for each year
#     pivot_df = agg_df.pivot(index="Segment", columns="Year", values=value_col).reset_index()
#
#     # Create figure
#     fig = go.Figure()
#
#     # Add bars for 2016
#     if 2016 in pivot_df.columns:
#         fig.add_trace(
#             go.Bar(
#                 x=pivot_df["Segment"],
#                 y=pivot_df[2016],
#                 name="Previous year",
#                 text=pivot_df[2016],
#                 textposition="outside",
#             )
#         )
#
#     # Add bars for 2017
#     if 2017 in pivot_df.columns:
#         fig.add_trace(
#             go.Bar(
#                 x=pivot_df["Segment"],
#                 y=pivot_df[2017],
#                 name="Current year",
#                 text=pivot_df[2017],
#                 textposition="outside",
#             )
#         )
#
#     # Layout
#     fig.update_layout(
#         barmode="group",
#         title="Current vs Previous Year by Segment",
#         xaxis_title=None,
#         yaxis_title=value_col,
#         bargap=0.25,
#     )
#
#     return fig

@capture("graph")
def line_profit_margin_vs_discount(data_frame):
    data_frame["Profit Margin"] = data_frame["Profit"] / data_frame["Sales"]
    discount_margin = data_frame.groupby("Discount", as_index=False)["Profit Margin"].mean()

    fig = px.line(
        discount_margin, x="Discount", y="Profit Margin", markers=True, title="Average Profit Margin vs Discount"
    )
    fig.update_layout(template="plotly_white")
    return fig


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
                            id="sales_by_segment",
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
                            figure=bar_chart_by_customer(
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
                            figure=bar_chart_by_customer(
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
        vm.Button(
            text="Export data",
            icon="download",
            actions=[va.export_data(targets=["sales_by_segment"], file_format="xlsx")],
            # description="Download data",
            variant="outlined",
        )
    ],
)

page_2 = vm.Page(
    title="Table",
    components=[vm.AgGrid(
        id="table_id",
        figure=custom_aggrid(superstore_df))
    ],
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
        )
    ]
)

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

