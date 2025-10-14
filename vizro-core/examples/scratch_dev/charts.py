"""Collection of custom charts."""

# import plotly.express as px

import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro.models.types import capture

PRIMARY_COLOR = "#1a85ff"
SECONDARY_COLOR = "#A0A2A8"
ORANGE_COLOR = "#f6c343"
GREEN_COLOR = "#60c96c"



@capture("graph")
def bar_chart_by_segment(data_frame, custom_data, value_col="Sales"):
    """Custom bar chart made with Plotly."""
    fig = px.bar(
        data_frame,
        y="Segment",
        x=value_col,
        color="Segment",
        title=f"{value_col} | By Customer",
        custom_data=custom_data,
        orientation="h",
    )
    return fig


@capture("graph")
def bar_chart_by_product(data_frame, custom_data, value_col="Sales"):
    """Custom bar chart made with Plotly."""
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
    """Custom bar chart made with Plotly."""
    # Handle aggregation depending on metric
    if value_col == "Order ID":
        subcat_metric = (
            data_frame.groupby("Sub-Category", as_index=False)["Order ID"].nunique()
            # .rename(columns={"Order ID": "Orders"}
            #         )
        )
        agg_col = "Order ID"
    else:
        subcat_metric = data_frame.groupby("Sub-Category", as_index=False)[value_col].sum()
        agg_col = value_col

    df_sorted = subcat_metric.sort_values(agg_col, ascending=True)

    fig = px.bar(
        df_sorted,
        y="Sub-Category",
        x=agg_col,
        orientation="h",
        title=f"{agg_col} | By Sub-Category",
        custom_data=custom_data,
    )
    fig.update_layout(
        title=dict(
            text=f"{agg_col} | By Sub-Category",
        ),
        yaxis=dict(
            visible=True,
            categoryorder="total ascending",  # ensure bars are ordered by metric
            title=None,
        ),
        xaxis=dict(title=None),
        showlegend=False,
    )

    return fig


@capture("graph")
def bar_chart_by_category(data_frame, custom_data, value_col="Sales", highlight_category=None):
    """Custom bar chart made with Plotly."""
    if value_col == "Order ID":
        category_metric = data_frame.groupby(["Category", "Sub-Category"], as_index=False)["Order ID"].nunique()
        agg_col = "Order ID"
    else:
        category_metric = data_frame.groupby(["Category", "Sub-Category"], as_index=False)[value_col].sum()
        agg_col = value_col

    if data_frame["Category"].nunique() > 1:
        x = "Category"
    else:
        x = "Sub-Category"

    fig = px.bar(
        category_metric,
        x=x,
        y=agg_col,
        title=f"{agg_col} | By {x} <br><sup> ⤵ Click on the category to drill-down to sub-category. Reset by using reset button on the right.</sup>",
        custom_data=custom_data,
    )

    fig.update_layout(
        yaxis=dict(visible=False),
        showlegend=False,
        bargap=0.6,
        xaxis_title=None,
        yaxis_title=None,
    )

    if highlight_category:
        for trace in fig.data:
            if trace.name == highlight_category:
                trace.opacity = 1
            else:
                trace.opacity = 0.2

    return fig


@capture("graph")
def bar_chart_by_customer(data_frame, value_col="Sales"):
    """Custom bar chart made with Plotly."""
    if value_col == "Order ID":
        df_grouped = data_frame.groupby("Customer Name", as_index=False)["Order ID"].nunique()
        agg_col = "Order ID"
    else:
        df_grouped = data_frame.groupby("Customer Name", as_index=False)[value_col].sum()
        agg_col = value_col

    df_top10 = df_grouped.nlargest(10, agg_col).reset_index(drop=True)
    df_top10["Rank"] = df_top10[agg_col].rank(method="first", ascending=False).astype(int)

    if agg_col in ["Sales", "Profit"]:
        df_top10["Value_Label"] = df_top10[agg_col].apply(lambda x: f"${x / 1000:.1f}K")
    else:
        df_top10["Value_Label"] = df_top10[agg_col].astype(str)

    fig = px.bar(
        df_top10,
        x=agg_col,
        y="Rank",
        orientation="h",
        color="Customer Name",
        color_discrete_sequence=[PRIMARY_COLOR],
        text="Value_Label",
    )

    fig.update_layout(
        title=f"{agg_col} | Top 10 Customers",
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

    fig.update_layout(
        title={
            "text": f"{agg_col} | Top 10 Customers",
        },
    )

    return fig


@capture("ag_grid")
def custom_aggrid(data_frame):
    """Custom aggrid table."""
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


@capture("graph")
def create_map_bubble_new(data_frame, custom_data, value_col="Sales"):
    """Custom map chart made with Plotly."""
    if value_col == "Order ID":
        state_metric = (
            data_frame.groupby(["State_Code", "Region"], as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        state_metric = (
            data_frame.groupby(["State_Code", "Region"], as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        state_metric = data_frame.groupby(["State_Code", "Region"], as_index=False)[value_col].sum()
        agg_col = value_col

    # Choropleth
    fig = px.choropleth(
        state_metric,
        locations="State_Code",
        locationmode="USA-states",
        color=agg_col,
        hover_name="Region",
        hover_data=["Region", agg_col],
        scope="usa",
        custom_data=custom_data,
        color_continuous_scale=['#d73027', '#e86b57', '#f49b8a', '#fac9bf', '#f7f7f7', '#8bc8fe', '#3595f4', '#0060d1', '#003096'],
        color_continuous_midpoint=0
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "bottom"}, "orientation": "h", "x": 0.5, "y": 0})

    return fig


@capture("graph")
def create_bar_chart_by_region(data_frame, value_col="Sales", highlight_region=None):
    """Custom bar chart made with Plotly."""
    if value_col == "Order ID":
        region_metric = (
            data_frame.groupby("Region", as_index=False)["Order ID"].nunique().rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        region_metric = (
            data_frame.groupby("Region", as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        region_metric = data_frame.groupby("Region", as_index=False)[value_col].sum()
        agg_col = value_col

    fig = px.bar(
        region_metric,
        y="Region",
        x=agg_col,
        orientation="h",
        color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR],
    )

    fig.update_layout(
        bargap=0.5,
        xaxis_title=None,
        yaxis_title=None,
        title=f"{agg_col} | By Region",
    )

    return fig


@capture("graph")
def create_line_chart_sales_per_month(data_frame, value_col="Sales"):
    """Custom line chart made with Plotly."""
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["YearMonth"] = data_frame["Order Date"].dt.to_period("M").astype(str)
    monthly_sales = data_frame.groupby("YearMonth", as_index=False)["Sales"].sum()

    fig = px.line(
        monthly_sales,
        x="YearMonth",
        y="Sales",
        #  markers=True,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


@capture("graph")
def create_bar_current_vs_previous_segment(data_frame, value_col="Sales"):
    """Custom bar chart made with Plotly."""
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["Year"] = data_frame["Order Date"].dt.year

    if value_col == "Order ID":
        agg_df = (
            data_frame.groupby(["Segment", "Year"], as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        agg_df = (
            data_frame.groupby(["Segment", "Year"], as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        agg_df = data_frame.groupby(["Segment", "Year"], as_index=False)[value_col].sum()
        agg_col = value_col

    pivot_df = agg_df.pivot(index="Segment", columns="Year", values=agg_col).reset_index()

    fig = go.Figure()

    if 2016 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[2016],
                name="Previous year",
                marker_color=SECONDARY_COLOR,
            )
        )

    if 2017 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[2017],
                name="Current year",
                marker_color=PRIMARY_COLOR,
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title=None,
        yaxis_title=None,
        bargap=0.4,
        title=f"{agg_col} | By Customer Segment",
        showlegend=False,
    )

    return fig


@capture("graph")
def create_bar_current_vs_previous_category(data_frame, value_col="Sales"):
    """Bar chart comparing current year vs previous year by category."""
    data_frame["Year"] = data_frame["Order Date"].dt.year

    if value_col == "Order ID":
        agg_df = (
            data_frame.groupby(["Category", "Year"], as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        agg_df = (
            data_frame.groupby(["Category", "Year"], as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        agg_df = data_frame.groupby(["Category", "Year"], as_index=False)[value_col].sum()
        agg_col = value_col

    pivot_df = agg_df.pivot(index="Category", columns="Year", values=agg_col).reset_index()

    fig = go.Figure()

    if 2016 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Category"],
                y=pivot_df[2016],
                name="Previous year",
                marker_color=SECONDARY_COLOR,
            )
        )

    if 2017 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Category"],
                y=pivot_df[2017],
                name="Current year",
                marker_color=PRIMARY_COLOR,
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title=None,
        yaxis_title=None,
        bargap=0.4,
        title=f"{agg_col} | By Product Category",
        showlegend=False,
    )

    return fig


@capture("graph")
def create_line_chart_sales_profit_per_month(data_frame):
    """Custom line chart made with Plotly."""
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["YearMonth"] = data_frame["Order Date"].dt.to_period("M").astype(str)
    monthly = data_frame.groupby("YearMonth", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["YearMonth"],
            y=monthly["Sales"],
            mode="lines+markers",
            name="Sales",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["YearMonth"],
            y=monthly["Profit"],
            mode="lines+markers",
            name="Profit",
            fill="tozeroy",
        )
    )

    fig.update_layout(
        title="Total Sales and Profit per Month",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


@capture("graph")
def create_line_chart_per_month(data_frame, value_col="Sales"):
    """Custom line chart made with Plotly."""
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["Year"] = data_frame["Order Date"].dt.year
    data_frame["Month"] = data_frame["Order Date"].dt.month

    if value_col == "Order ID":
        monthly = (
            data_frame.groupby(["Year", "Month"], as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        monthly = (
            data_frame.groupby(["Year", "Month"], as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        monthly = data_frame.groupby(["Year", "Month"], as_index=False)[value_col].sum()
        agg_col = value_col

    prev_year = monthly[monthly["Year"] == 2016]
    curr_year = monthly[monthly["Year"] == 2017]

    fig = go.Figure()
    # Add Previous Year first so it renders at the bottom
    fig.add_trace(
        go.Scatter(
            x=prev_year["Month"],
            y=prev_year[agg_col],
            fill="tozeroy",
            name="Previous Year",
            marker_color=SECONDARY_COLOR,
        )
    )
    # Add Current Year second so it renders on top
    fig.add_trace(
        go.Scatter(
            x=curr_year["Month"],
            y=curr_year[agg_col],
            name="Current Year",
            marker_color=PRIMARY_COLOR,
            fill="tozeroy",
        )
    )

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            title=None,
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        ),
        yaxis_title=None,
        title=f"{agg_col} | By Month",
        legend=dict(yanchor="top", y=1.2, xanchor="right", x=1),
    )

    return fig


@capture("graph")
def create_top_10_states(data_frame, value_col="Sales"):
    """Custom bar chart made with Plotly."""
    state_sales = data_frame.groupby(["State"], as_index=False)["Sales"].sum()
    state_sales["Rank"] = state_sales.groupby("State")["Sales"].rank(method="first", ascending=False)

    top_states = state_sales[state_sales["Rank"] <= 10]

    fig = px.bar(
        top_states,
        x=value_col,
        y="State",
        orientation="h",
        color_discrete_sequence=[PRIMARY_COLOR],
        title=f"Top 10 States by {value_col}",
    )

    fig.update_yaxes(categoryorder="total ascending")
    return fig




@capture("graph")
def bar_chart_by_state(data_frame, value_col="Sales"):
    """Custom bar chart made with Plotly."""
    if value_col == "Order ID":
        df_grouped = (
            data_frame.groupby("State", as_index=False)["Order ID"].nunique().rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    else:
        df_grouped = data_frame.groupby("State", as_index=False)[value_col].sum()
        agg_col = value_col

    df_top10 = df_grouped.nlargest(10, agg_col).reset_index(drop=True)
    df_top10["Rank"] = df_top10[agg_col].rank(method="first", ascending=False).astype(int)

    if agg_col in ["Sales", "Profit"]:
        df_top10["Value_Label"] = df_top10[agg_col].apply(lambda x: f"${x / 1000:.1f}K")
    else:
        df_top10["Value_Label"] = df_top10[agg_col].astype(str)

    fig = px.bar(
        df_top10,
        x=agg_col,
        y="Rank",
        orientation="h",
        text="Value_Label",
        color_discrete_sequence=[PRIMARY_COLOR],
    )

    fig.update_layout(
        title=f"<b>{agg_col}</b> | Top 10 States",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(
            tickmode="array",
            tickvals=df_top10["Rank"],
            ticktext=[f"{s}" for s in df_top10["State"]],
            autorange="reversed",
        ),
        showlegend=False,
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        title={
            "text": f"<b>{agg_col}</b> | Top 10 States",
            "y": 1,
            "yanchor": "top",
        },
    )

    return fig


@capture("graph")
def pie_chart_by_order_status(data_frame, value_col="Sales"):
    """Pie chart showing distribution by Order Status."""
    if value_col == "Order ID":
        status_metric = (
            data_frame.groupby("Order Status", as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    elif value_col == "Customer ID":
        status_metric = (
            data_frame.groupby("Order Status", as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        status_metric = data_frame.groupby("Order Status", as_index=False)[value_col].sum()
        agg_col = value_col

    fig = px.pie(
        status_metric,
        names="Order Status",
        values=agg_col,
        color="Order Status",
        title=f"{agg_col} by Order Status",
        color_discrete_map={"In Transit": PRIMARY_COLOR, "Processing": ORANGE_COLOR, "Delivered": GREEN_COLOR},
        hole=0.6,
    )

    fig.update_layout(
        title=dict(
            text=f"{agg_col} | By Order Status",
        ),
        legend=dict(yanchor="bottom", y=-0.2, xanchor="right", orientation="v"),
    )

    return fig



@capture("graph")
def scatter_with_quadrants(
    x: str,
    y: str,
    custom_data: list[str],
    x_ref_quantile: float = 0.5,
    y_ref_quantile: float = 0.2,
    data_frame: pd.DataFrame = None,
    highlight_product=None,
):
    """Custom scatter plot with quadrants made with Plotly."""
    fig = px.scatter(
        data_frame=data_frame,
        x=x,
        y=y,
        custom_data=custom_data,
        color="Product Name",
        color_discrete_sequence=["grey"],
        size="Profit Absolute",
        size_max=20,
        opacity=0.6,
        hover_data=["Product Name", "Profit", "Sales", "Profit Margin"],
        title=f"{data_frame['Category / Sub-Category'].iloc[0]} <br><sup> ⤵ Click on a point to filter the table. Refresh the page to deselect.</sup>",
    )

    if highlight_product:
        for trace in fig.data:
            if trace.name == highlight_product:
                trace.marker.color = "orange"

    # Add reference lines to figure
    x_reference_line = data_frame[x].quantile(x_ref_quantile)
    y_reference_line = data_frame[y].quantile(y_ref_quantile)
    fig.add_hline(y=y_reference_line, line_dash="dash", line_color="grey")
    fig.add_vline(x=x_reference_line, line_dash="dash", line_color="grey")

    # Add quadrants to figure
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=x_reference_line,
        y0=data_frame[y].max() + 700,
        x1=data_frame[x].max() + 700,
        y1=y_reference_line,
        fillcolor="#00b4ff",
        line_width=0,
        opacity=0.4,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=data_frame[x].min(),
        y0=y_reference_line,
        x1=x_reference_line,
        y1=data_frame[y].max() + 700,
        fillcolor="#00b4ff",
        line_width=0,
        opacity=0.2,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=data_frame[x].min(),
        y0=data_frame[y].min() - 700,
        x1=x_reference_line,
        y1=y_reference_line,
        fillcolor="#ff9222",
        line_width=0,
        opacity=0.4,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=x_reference_line,
        y0=data_frame[y].min() - 700,
        x1=data_frame[x].max() + 700,
        y1=y_reference_line,
        fillcolor="#ff9222",
        line_width=0,
        opacity=0.2,
        layer="below",
    )

    # Customize hovertemplate
    fig.update_layout(title_pad_t=24)
    fig.update_traces(
        showlegend=False,
        hovertemplate="<br>".join(
            [
                "%{customdata[0]}",
                "Profit: %{y:$,.2f}",
                "Sales: %{x:$,.2f}",
            ]
        )
        + "<extra></extra>",
    )

    return fig


@capture("graph")
def scatter_with_quadrants_subc(
    x: str,
    y: str,
    custom_data: list[str],
    x_ref_quantile: float = 0.5,
    y_ref_quantile: float = 0.2,
    data_frame: pd.DataFrame = None,
    highlight_sub_category=None,
):
    """Custom scatter plot with quadrants grouped by Sub-Category."""
    fig = px.scatter(
        data_frame=data_frame,
        x=x,
        y=y,
        custom_data=custom_data,
        color="Sub-Category",
        color_discrete_sequence=["grey"],
        size="Profit Absolute",
        size_max=20,
        opacity=0.7,
        hover_data=["Sub-Category", "Profit", "Sales", "Profit Margin"],
        title="Sub-Categories <br><sup> ⤵ Click on a point to filter the table. Refresh the page to deselect.</sup>",
    )

    if highlight_sub_category is not None:
        mask = data_frame["Sub-Category"] == highlight_sub_category
        if mask.any():
            profit_values = data_frame.loc[mask, "Profit Absolute"]
            max_profit = data_frame["Profit Absolute"].max()
            marker_sizes = (profit_values / max_profit * 40).clip(lower=6)

            fig.add_scatter(
                x=data_frame.loc[mask, x],
                y=data_frame.loc[mask, y],
                mode="markers+text",
                text=[highlight_sub_category],
                marker=dict(color="orange", size=marker_sizes, line=dict(width=2, color="black")),
                hovertext=highlight_sub_category,
                textposition="bottom center",
            )

    # Reference lines (based on all data)
    x_reference_line = data_frame[x].quantile(x_ref_quantile)
    y_reference_line = data_frame[y].quantile(y_ref_quantile)
    fig.add_hline(y=y_reference_line, line_dash="dash", line_color="grey")
    fig.add_vline(x=x_reference_line, line_dash="dash", line_color="grey")

    # Quadrant shading
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=x_reference_line,
        y0=data_frame[y].max() + 700,
        x1=data_frame[x].max() + 700,
        y1=y_reference_line,
        fillcolor="#00b4ff",
        line_width=0,
        opacity=0.4,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=data_frame[x].min(),
        y0=y_reference_line,
        x1=x_reference_line,
        y1=data_frame[y].max() + 700,
        fillcolor="#00b4ff",
        line_width=0,
        opacity=0.2,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=data_frame[x].min(),
        y0=data_frame[y].min() - 700,
        x1=x_reference_line,
        y1=y_reference_line,
        fillcolor="#ff9222",
        line_width=0,
        opacity=0.4,
        layer="below",
    )
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=x_reference_line,
        y0=data_frame[y].min() - 700,
        x1=data_frame[x].max() + 700,
        y1=y_reference_line,
        fillcolor="#ff9222",
        line_width=0,
        opacity=0.2,
        layer="below",
    )

    # Hover and legend tweaks
    fig.update_traces(
        showlegend=False,
        hovertemplate="<br>".join(
            [
                "%{customdata[0]}",
                "Sub-Category: %{marker.color}",
                "Profit: %{y:$,.2f}",
                "Sales: %{x:$,.2f}",
            ]
        )
        + "<extra></extra>",
    )

    fig.update_layout(
        title_pad_t=24,
        legend_title_text="Sub-Category",  # ✅ clearer legend
        legend=dict(itemsizing="trace", orientation="h", yanchor="bottom", y=-0.3),
    )

    return fig


@capture("graph")
def pareto_customers_chart(data_frame, value_col="Sales", highlight_customer=None):
    """Custom chart made with Plotly."""
    customer_df = (
        data_frame.groupby("Customer Name", as_index=False)[value_col].sum().sort_values(by=value_col, ascending=False)
    )

    # 2️⃣ Compute cumulative metrics
    customer_df["Cumulative Value"] = customer_df[value_col].cumsum()
    total_value = customer_df[value_col].sum()
    customer_df["Cumulative % Value"] = 100 * customer_df["Cumulative Value"] / total_value

    customer_df["Customer Rank"] = range(1, len(customer_df) + 1)
    customer_df["Cumulative % Customers"] = 100 * customer_df["Customer Rank"] / len(customer_df)

    thresholds = {
        "A": 20,
        "B": 50,
        "C": 100,
    }

    def assign_segment(cust_pct):
        if cust_pct <= thresholds["A"]:
            return "A"
        elif cust_pct <= thresholds["B"]:
            return "B"
        else:
            return "C"

    customer_df["Segment"] = customer_df["Cumulative % Customers"].apply(assign_segment)
    segment_colors = {"A": "#00b4ff", "B": "#00b4ff", "C": "#00b4ff"}

    fig = px.line(
        customer_df,
        x="Cumulative % Customers",
        y="Cumulative % Value",
        markers=True,
        title=f"Pareto Analysis of Customers ({value_col})",
        hover_data=["Customer Name", value_col, "Cumulative % Value"],
        color_discrete_sequence=["orange"],
    )
    fig.update_traces(showlegend=False)
    fig.add_vrect(x0=0, x1=thresholds["A"], fillcolor=segment_colors["A"], opacity=0.6, layer="below")
    fig.add_vrect(x0=thresholds["A"], x1=thresholds["B"], fillcolor=segment_colors["B"], opacity=0.3, layer="below")
    fig.add_vrect(x0=thresholds["B"], x1=100, fillcolor=segment_colors["C"], opacity=0.1, layer="below")

    if highlight_customer and highlight_customer in customer_df["Customer Name"].values:
        cust = customer_df[customer_df["Customer Name"] == highlight_customer].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[cust["Cumulative % Customers"]],
                y=[cust["Cumulative % Value"]],
                mode="markers+text",
                text=[highlight_customer],
                textposition="bottom right",
                marker=dict(color="orange", size=12, line=dict(width=2)),
                showlegend=False,
            )
        )

    fig.update_layout(
        xaxis_title="% of Total Customers",
        yaxis_title=f"Cumulative % of {value_col}",
        yaxis=dict(range=[0, 105]),
        xaxis=dict(range=[0, 105]),
        hovermode="x unified",
    )

    return fig


CELL_STYLE_PRODUCT = {
    "styleConditions": [
        {
            "condition": "params.value < -0.1",
            "style": {"backgroundColor": "#ff9222"},
        },
        {
            "condition": "params.value >= -0.1 && params.value <= 0",
            "style": {"backgroundColor": "#ffba7f"},
        },
        {
            "condition": "params.value > 0 && params.value <= 0.05",
            "style": {"backgroundColor": "#e4e4e4"},
        },
        {
            "condition": "params.value > 0.05 && params.value <= 0.15",
            "style": {"backgroundColor": "#b7d4ee"},
        },
        {
            "condition": "params.value > 0.15 && params.value <= 0.20",
            "style": {"backgroundColor": "#80c4f6"},
        },
        {
            "condition": "params.value > 0.20",
            "style": {"backgroundColor": "#00b4ff"},
        },
    ]
}


COLUMN_DEFS_PRODUCT = [
    # {"field": "Product Name", "cellDataType": "text", "headerName": "Product", "flex": 3},
    {"field": "Sub-Category", "cellDataType": "text", "headerName": "Sub-Category", "flex": 3},
    {
        "field": "Profit",
        "cellDataType": "number",
        "flex": 2,
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
    },
    {
        "field": "Sales",
        "cellDataType": "number",
        "flex": 2,
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
    },
    {
        "field": "Profit Margin",
        "flex": 2,
        "cellDataType": "number",
        "valueFormatter": {"function": "d3.format('.0%')(params.value)"},
        "cellStyle": CELL_STYLE_PRODUCT,
    },
]


@capture("graph")
def treemap_chart(
    data_frame: pd.DataFrame,
    path: list,
    values: str,
    color: str = None,
    title: str = None,
):
    """Custom treemap chart made with Plotly."""
    fig = px.treemap(
        data_frame=data_frame,
        path=path,
        values=values,
        color=color if color else values,
        hover_data={values: ":$,.2f", color: ":$,.2f" if color else False},
        title=title or f"Treemap of {values} by {' > '.join(path)}",
    )
    fig.update_coloraxes(colorbar={"thickness": 10})

    return fig


@capture("graph")
def bar_chart_by_category_h(data_frame, custom_data, value_col="Sales", highlight_category=None):
    """Custom bar chart made with Plotly."""
    df_sorted = data_frame.sort_values(value_col, ascending=True)
    fig = px.bar(
        df_sorted,
        x="Category",
        y=value_col,
        color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR],
        title=f"{value_col} | By Category",
        custom_data=custom_data,
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(bargap=0.4, xaxis_title=None, yaxis_title=None)

    if highlight_category:
        for trace in fig.data:
            if trace.name == highlight_category:
                trace.opacity = 1
            else:
                trace.opacity = 0.2

    return fig


CELL_STYLE_CUSTOMERS = {
    "styleConditions": [
        {
            "condition": "params.value < -0.1",
            "style": {"backgroundColor": "#ff9222"},
        },
        {
            "condition": "params.value >= -0.1 && params.value <= 0",
            "style": {"backgroundColor": "#ffba7f"},
        },
        {
            "condition": "params.value > 0 && params.value <= 0.05",
            "style": {"backgroundColor": "#e4e4e4"},
        },
        {
            "condition": "params.value > 0.05 && params.value <= 0.15",
            "style": {"backgroundColor": "#b7d4ee"},
        },
        {
            "condition": "params.value > 0.15 && params.value <= 0.20",
            "style": {"backgroundColor": "#80c4f6"},
        },
        {
            "condition": "params.value > 0.20",
            "style": {"backgroundColor": "#00b4ff"},
        },
    ]
}


COLUMN_DEFS_CUSTOMERS = [
    {"field": "Rank", "cellDataType": "number", "headerName": "Rank", "flex": 2},
    {
        "field": "Customer Name",
        "cellDataType": "text",
        "flex": 3,
        # "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
    },
    {
        "field": "Sales",
        "cellDataType": "number",
        "flex": 3,
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
    },
    {
        "headerName": "Cumulative %",
        "field": "Cumulative %",
        "type": "numericColumn",
        "valueFormatter": {"function": "d3.format('.1f')(params.value) + '%'"},
        "width": 130,
    },
]


@capture("graph")
def bar_chart_top_n(data_frame, x="Sales", y="City", top_n=10):
    """Generic bar chart to show top N by any dimension."""
    # TODO: Needs to be fixed when prefiltered on city. Otherwise, top N is not properly recalculated
    # after clicking on a state.
    df_top = data_frame.groupby(y).agg({x: "sum"}).sort_values(x, ascending=False).head(top_n).reset_index()

    # Sort ascending so highest appears at top in horizontal bar chart
    df_top = df_top.sort_values(x, ascending=True)

    # Create bar chart
    fig = px.bar(
        df_top,
        x=x,
        y=y,
        orientation="h",
        color_discrete_sequence=[PRIMARY_COLOR],
        title=f"Top {top_n} {y} by {x}",
    )

    return fig


@capture("graph")
def bar_chart_top_customers(data_frame, value_col="Sales", top_x=10):
    """Custom bar chart made with Plotly."""
    if value_col == "Order ID":
        customer_metric = (
            data_frame.groupby("Customer Name", as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    if value_col == "Customer ID":
        customer_metric = (
            data_frame.groupby("Customer Name", as_index=False)["Customer ID"]
            .nunique()
            .rename(columns={"Customer ID": "Customers"})
        )
        agg_col = "Customers"
    else:
        customer_metric = data_frame.groupby("Customer Name", as_index=False)[value_col].sum()
        agg_col = value_col

    df_top10 = customer_metric.nlargest(top_x, agg_col).reset_index(drop=True)
    df_top10["Rank"] = df_top10[agg_col].rank(method="first", ascending=False).astype(int)

    if agg_col in ["Sales", "Profit"]:
        df_top10["Label"] = df_top10[agg_col].apply(lambda x: f"${x / 1000:.1f}K")
    else:
        df_top10["Label"] = df_top10[agg_col].apply(lambda x: f"{x:,}")

    fig = px.bar(
        df_top10,
        x=agg_col,
        y="Rank",
        orientation="h",
        color="Customer Name",
        text="Label",
        color_discrete_sequence=["#4dabf7"],
        title=f"Top {top_x} Customers by {agg_col}",
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(
            tickmode="array",
            tickvals=df_top10["Rank"],
            ticktext=[f"{c}" for c in df_top10["Customer Name"]],
            autorange="reversed",
            tickfont=dict(size=13),
        ),
    )

    fig.update_yaxes(ticklabelposition="outside left")
    fig.update_traces(textposition="outside")

    return fig


@capture("ag_grid")
def custom_orders_aggrid(data_frame):
    """Custom aggrid table."""
    data_frame["Profit Ratio"] = (data_frame["Profit"] / data_frame["Sales"]).round(3)
    column_defs_orders = [
        {"headerName": "Order ID", "field": "Order ID", "minWidth": 150},
        {
            "headerName": "Segment",
            "field": "Segment",
            "minWidth": 140,
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": "params.value === 'Corporate'",
                        "style": {
                            "backgroundColor": "#37474F",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "params.value === 'Consumer'",
                        "style": {
                            "backgroundColor": "#546E7A",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "params.value === 'Home Office'",
                        "style": {
                            "backgroundColor": "#8D8D8D",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                ]
            },
        },
        {"headerName": "Customer Name", "field": "Customer Name", "minWidth": 170},
        {"headerName": "Location", "field": "City", "minWidth": 150},
        {
            "headerName": "Category",
            "field": "Category",
            "minWidth": 150,
            "cellRenderer": {
                "function": """
                function(params) {
                    if (params.value === 'Furniture') {
                        return '<span><i class="material-symbols-outlined">chair</i>' + params.value + '</span>';
                    }
                    if (params.value === 'Technology') {
                        return '<span><i class="material-symbols-outlined">laptop_mac</i>' + params.value + '</span>';
                    }
                    if (params.value === 'Office Supplies') {
                        return '<span><i class="material-symbols-outlined">assignment</i>' + params.value + '</span>';
                    }
                }
                """
            },
        },
        {"headerName": "Sales", "field": "Sales", "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"}},
        {
            "headerName": "Profit",
            "field": "Profit",
            "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        },
        {
            "headerName": "Profit Ratio",
            "field": "Profit Ratio",
            "minWidth": 140,
            "valueFormatter": {"function": "d3.format('.1%')(params.value)"},
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": "Number(params.value) < 0",
                        "style": {
                            "backgroundColor": "#c42f3e",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0 && Number(params.value) < 0.10",
                        "style": {
                            "backgroundColor": "#E04A55",
                            "color": "black",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0.10 && Number(params.value) < 0.15",
                        "style": {
                            "backgroundColor": "#F2A3A9",
                            "color": "black",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0.15 && Number(params.value) < 0.25",
                        "style": {
                            "backgroundColor": "#C8E6C9",
                            "color": "black",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0.25 && Number(params.value) < 0.35",
                        "style": {
                            "backgroundColor": "#81C784",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0.35",
                        "style": {
                            "backgroundColor": "#4CAF50",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px 12px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "38px",
                        },
                    },
                ]
            },
        },
    ]

    aggrid = AgGrid(
        columnDefs=column_defs_orders,
        defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 30, "flex": 1},
        style={"height": "800px", "width": "100%"},
        rowData=data_frame.to_dict("records"),
        dashGridOptions={
            "rowHeight": 55,
            "animateRows": True,
            "suppressMovableColumns": True,
            "pagination": True,
            "paginationPageSize": 20,
        },
        dangerously_allow_code=True,
    )
    return aggrid
