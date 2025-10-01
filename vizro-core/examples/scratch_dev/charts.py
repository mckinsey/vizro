"""Collection of custom charts."""

# import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro.models.types import capture


@capture("graph")
def create_map_bubble(data_frame, value_col="Sales"):
    data_frame[value_col] = data_frame[value_col].abs()
    fig = px.scatter_geo(
        data_frame,
        locations="State_Code",
        locationmode="USA-states",
        size=value_col,
        hover_name="State",
        hover_data={value_col: ":$,.0f", "State_Code": False},
        size_max=40,
        title=f"{value_col} | By State",
        scope="usa",
    )

    fig.update_layout(
        title={
            "text": f"{value_col} | By State",
            "x": 0.5,
            "xanchor": "center",
        },
        geo=dict(
            showlakes=True,
            projection_type="albers usa",
            showframe=True,
            showcoastlines=True,
            showsubunits=True,
        ),
    )

    return fig


@capture("graph")
def bar_chart_by_segment(data_frame, custom_data, value_col="Sales"):
    fig = px.bar(
        data_frame,
        y="Segment",
        x=value_col,
        color="Segment",
        title=f"{value_col} | By Segment",
        custom_data=custom_data,
        orientation="h",
    )

    fig.update_layout(title=dict(x=0.5, xanchor="center"), showlegend=False)
    fig.update_layout(bargap=0.6, xaxis_title=None)
    return fig


@capture("graph")
def pie_chart_by_segment(data_frame, custom_data, value_col="Sales"):
    fig = px.pie(
        data_frame,
        names="Segment",
        values=value_col,
        color="Segment",
        title=f"{value_col} | By Segment",
        custom_data=custom_data,
        hole=0.3,  # optional: makes it a donut chart
    )

    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    return fig


@capture("graph")
def pie_chart_by_category(data_frame, custom_data, value_col="Sales"):
    fig = px.pie(
        data_frame,
        names="Category",
        values=value_col,
        color="Category",
        title=f"{value_col} | By Category",
        custom_data=custom_data,
        hole=0.3,  # optional: makes it a donut chart
    )

    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    return fig


@capture("graph")
def bar_chart_by_product(data_frame, custom_data, value_col="Sales"):
    df_grouped = data_frame.groupby("Product Name", as_index=False)[value_col].sum()
    df_top10 = df_grouped.nlargest(10, value_col).reset_index(drop=True)
    df_top10["Rank"] = df_top10[value_col].rank(method="first", ascending=False).astype(int)
    df_top10 = df_top10.sort_values("Rank")
    df_top10["Sales_Label"] = df_top10[value_col].apply(lambda x: f"${x / 1000:.1f}K")

    fig = px.bar(
        df_top10,
        x=value_col,
        y="Rank",
        orientation="h",
        color="Product Name",
        color_discrete_sequence=["#4dabf7"] + ["#ff9222"] * 9,
        custom_data=custom_data,
    )

    fig.update_layout(
        title="<b>Sales</b> | By Product",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(
            tickmode="array",
            tickvals=df_top10["Rank"],
            autorange="reversed",  # Rank 1 on top
        ),
        showlegend=False,
    )

    fig.update_traces(textposition="outside")

    return fig


@capture("graph")
def bar_chart_by_subcategory(data_frame, custom_data, value_col="Sales"):
    df_sorted = data_frame.sort_values(value_col, ascending=True)
    fig = px.bar(
        df_sorted,
        y="Sub-Category",
        x=value_col,
        orientation="h",
        title=f"{value_col} | By Sub-Category",
        custom_data=custom_data,
    )

    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        yaxis=dict(visible=True, categoryorder="total ascending"),  # order bars by Sales
        showlegend=False,
    )
    return fig


@capture("graph")
def bar_chart_by_category(data_frame, custom_data, value_col="Sales"):
    fig = px.bar(
        data_frame,
        x="Category",
        y=value_col,
        title=f"{value_col} | By Category",
        color="Category",
        custom_data=custom_data,
    )
    fig.update_layout(title=dict(x=0.5, xanchor="center"), yaxis=dict(visible=False), showlegend=False)
    fig.update_layout(bargap=0.6, xaxis_title=None, yaxis_title=None)
    return fig


@capture("graph")
def bar_chart_sales_by_customer(data_frame, value_col="Sales"):
    df_grouped = data_frame.groupby("Customer Name", as_index=False)[value_col].sum()
    df_top10 = df_grouped.nlargest(10, value_col).reset_index(drop=True)
    df_top10["Rank"] = df_top10[value_col].rank(method="first", ascending=False).astype(int)
    df_top10["Sales_Label"] = df_top10[value_col].apply(lambda x: f"${x / 1000:.1f}K")

    fig = px.bar(
        df_top10,
        x=value_col,
        y="Rank",
        orientation="h",
        # text="Sales_Label",
        color="Customer Name",
        color_discrete_sequence=["#4dabf7"] + ["#ff9222"] * 9,  # Highlight top 1
        # custom_data=custom_data,
    )

    fig.update_layout(
        title=f"<b>{value_col}</b> | Top 10 Customers",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(
            tickmode="array",
            tickvals=df_top10["Rank"],
            ticktext=[f"{r} | {c}" for r, c in zip(df_top10["Rank"], df_top10["Customer Name"])],
            autorange="reversed",
        ),
        showlegend=False,
    )

    fig.update_traces(textposition="outside")

    return fig


@capture("ag_grid")
def custom_aggrid(data_frame):
    data_frame["Profit Ratio"] = (data_frame["Profit"] / data_frame["Sales"]).round(3)

    column_defs = [
        {"headerName": "Customer Name", "field": "Customer Name"},
        {"headerName": "Segment", "field": "Segment"},
        {"headerName": "Category", "field": "Category"},
        {"headerName": "Sub-Category", "field": "Sub-Category"},
        {"headerName": "Product Name", "field": "Product Name"},
        {"headerName": "Sales", "field": "Sales", "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"}},
        {"headerName": "Quantity", "field": "Quantity", "cellStyle": {"textAlign": "center"}},
        {
            "headerName": "Profit",
            "field": "Profit",
            "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
            "cellStyle": {
                "function": """
                function(params) {
                    if (params.value < 0) {
                        return {color: 'red', fontWeight: 'bold'};
                    } else {
                        return {color: 'green', fontWeight: 'bold'};
                    }
                }
                """
            },
        },
        {
            "headerName": "Profit Ratio",
            "field": "Profit Ratio",
            "valueFormatter": {"function": "d3.format('.1%')(params.value)"},
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": "params.value < 0.5",
                        "style": {"color": "red", "fontWeight": "bold"},
                    },
                    {
                        "condition": "params.value >= 0.5",
                        "style": {"color": "green", "fontWeight": "bold"},
                    },
                ]
            },
        },
    ]
    aggrid = AgGrid(
        columnDefs=column_defs,
        defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 30, "flex": 1},
        style={"height": "750px", "width": "100%"},
        rowData=data_frame.to_dict("records"),
        dashGridOptions={"pagination": True, "paginationPageSize": 20},
    )
    return aggrid


#
# @capture("graph")
# def bar_chart_by_segment_w_bm(data_frame, custom_data, value_col="Sales"):
#     # Copy and prepare
#     df = data_frame.copy()
#     df["Order Date"] = pd.to_datetime(df["Order Date"])
#     df["Year"] = df["Order Date"].dt.year
#
#     # Latest two years
#     latest_year = df["Year"].max()
#     prev_year = latest_year - 1
#
#     # Aggregate current year sales
#     current_sales = df[df["Year"] == latest_year].groupby("Segment")[value_col].sum()
#
#     # Aggregate current and previous year profit
#     current_profit = df[df["Year"] == latest_year].groupby("Segment")["Profit"].sum()
#     prev_profit = df[df["Year"] == prev_year].groupby("Segment")["Profit"].sum()
#
#     # Create plotting dataframe
#     merged = current_sales.reset_index().rename(columns={value_col: "Sales"})
#     merged["CurrentProfit"] = merged["Segment"].map(current_profit)
#     merged["PrevProfit"] = merged["Segment"].map(prev_profit)
#
#     # Plot bars (Sales)
#     fig = px.bar(
#         merged,
#         x="Segment",
#         y="Sales",
#         color="Segment",
#         title=f"{value_col} | By Segment",
#         custom_data=custom_data,
#     )
#
#     # Add benchmarks (previous year profit) + annotations
#     for i, row in merged.iterrows():
#         seg = row["Segment"]
#         current = row["CurrentProfit"]
#         prev = row["PrevProfit"]
#
#         # Benchmark line = previous year profit
#         fig.add_shape(
#             type="line",
#             x0=seg, x1=seg,
#             y0=prev, y1=prev,
#             line=dict(color="darkblue", width=4),
#             xref="x", yref="y"
#         )
#
#         # Growth %
#         growth = (current - prev) / prev * 100 if pd.notna(prev) and prev != 0 else 0
#
#         # Annotation (sales + growth %)
#         fig.add_annotation(
#             x=seg,
#             y=row["Sales"],
#             text=f"<b>${row['Sales'] / 1000:,.1f}K</b><br>"
#                  f"<span style='color:{'green' if growth >= 0 else 'red'}'>▲ {growth:.1f}%</span>",
#             showarrow=False,
#             yshift=20,
#             align="center"
#         )
#
#     # Layout tweaks
#     fig.update_layout(
#         title=dict(x=0.5, xanchor="center"),
#         yaxis=dict(visible=False),
#         showlegend=False,
#         bargap=0.6,
#         xaxis_title=None,
#         yaxis_title=None,
#     )
#
#     return fig


@capture("graph")
def create_map_bubble_new(data_frame, custom_data, value_col="Sales"):
    state_profit = data_frame.groupby(["State_Code", "Region"], as_index=False)[value_col].sum()
    fig = px.choropleth(
        state_profit,
        locations="State_Code",
        locationmode="USA-states",
        color=value_col,
        hover_name="State_Code",
        hover_data=["Region", value_col],
        scope="usa",
        custom_data=custom_data,
    )

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return fig


@capture("graph")
def create_bar_chart_by_region(data_frame, value_col="Sales", highlight_region=None):
    # region_colors = {"West": "#ff9222", "East": "#474EA6", "South": "#4dabf7", "Central": "#fa5252"}
    region_sales = data_frame.groupby("Region", as_index=False)[value_col].sum()
    fig = px.bar(
        region_sales,
        y="Region",
        x=value_col,
        color="Region",
        # text="Sales",  # show sales values on bars
        orientation="h",
        # color_discrete_map=region_colors,
    )

    # Improve layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        bargap=0.6,
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
    )
    if highlight_region:
        if highlight_region == [None]:
            for trace in fig.data:
                trace.marker.opacity = 1
        else:
            for trace in fig.data:
                if trace.name == highlight_region:
                    trace.marker.opacity = 1
                else:
                    trace.marker.opacity = 0.2

    return fig


@capture("graph")
def create_line_chart_sales_per_month(data_frame, value_col="Sales"):
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])

    # Extract year-month for grouping
    data_frame["YearMonth"] = data_frame["Order Date"].dt.to_period("M").astype(str)

    # Aggregate sales by month
    monthly_sales = data_frame.groupby("YearMonth", as_index=False)["Sales"].sum()

    # Create line chart
    fig = px.line(
        monthly_sales,
        x="YearMonth",
        y="Sales",
        markers=True,
        # title="Total Sales by Month"
    )

    # Improve layout
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=20, b=20),
        # xaxis=dict(tickangle=45)
    )
    return fig


@capture("graph")
def create_bar_sales_vs_profit_category(data_frame, value_col="Sales"):
    agg_df = data_frame.groupby("Category", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    # Melt the data so we can plot Sales and Profit side by side
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


@capture("graph")
def create_bar_current_vs_previous_segment(data_frame, value_col="Sales"):
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["Year"] = data_frame["Order Date"].dt.year

    # Aggregate by Segment + Year
    agg_df = data_frame.groupby(["Segment", "Year"], as_index=False).agg({value_col: "sum"})

    # Pivot to get separate columns for each year
    pivot_df = agg_df.pivot(index="Segment", columns="Year", values=value_col).reset_index()

    # Create figure
    fig = go.Figure()

    # Add bars for 2016
    if 2016 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[2016],
                name="Previous year",
                text=pivot_df[2016],
                textposition="outside",
            )
        )

    # Add bars for 2017
    if 2017 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[2017],
                name="Current year",
                text=pivot_df[2017],
                textposition="outside",
            )
        )

    # Layout
    fig.update_layout(
        barmode="group",
        title="Current vs Previous Year by Segment",
        xaxis_title=None,
        yaxis_title=value_col,
        bargap=0.25,
    )

    return fig


@capture("graph")
def create_line_chart_sales_profit_per_month(data_frame):
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])

    # Extract year-month for grouping
    data_frame["YearMonth"] = data_frame["Order Date"].dt.to_period("M").astype(str)

    # Aggregate sales and profit by month
    monthly = data_frame.groupby("YearMonth", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    # Create line for Sales
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["YearMonth"],
            y=monthly["Sales"],
            mode="lines+markers",
            name="Sales",
        )
    )

    # Create line for Profit with shaded area
    fig.add_trace(
        go.Scatter(
            x=monthly["YearMonth"],
            y=monthly["Profit"],
            mode="lines+markers",
            name="Profit",
            fill="tozeroy",  # Shade area below profit line
        )
    )

    # Improve layout
    fig.update_layout(
        title="Total Sales and Profit per Month",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


@capture("graph")
def line_profit_margin_vs_discount(data_frame):
    # Compute profit margin
    data_frame["Profit Margin"] = data_frame["Profit"] / data_frame["Sales"]

    # Aggregate
    discount_margin = data_frame.groupby("Discount", as_index=False)["Profit Margin"].mean()

    fig = px.line(
        discount_margin, x="Discount", y="Profit Margin", markers=True, title="Average Profit Margin vs Discount"
    )
    fig.update_layout(template="plotly_white")
    return fig


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
def create_line_chart_per_month(data_frame, value_col="Sales"):
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
