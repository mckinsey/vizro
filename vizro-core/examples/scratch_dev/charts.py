"""Collection of custom charts."""

import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro.models.types import capture

CURRENT_YEAR = 2017
PREVIOUS_YEAR = 2016

PRIMARY_COLOR = "#2251ff"
SECONDARY_COLOR = "#A0A2A8"
ORANGE_COLOR = "#f6c343"
GREEN_COLOR = "#60c96c"
RED_COLOR = "#f17e7e"
DIVERGING_RED_GREEN = [
    "#a84545",
    "#b82525",
    "#e33b3b",
    "#f17e7e",
    "#e6d7bc",
    "#75f0e7",
    "#0bdacb",
    "#13b8ab",
    "#108980",
]
DIVERGING_RED_BLUE = [
    "#a84545",
    "#b82525",
    "#e33b3b",
    "#f17e7e",
    "#e6e6e6",
    "#99c4ff",
    "#2251ff",
    "#061f79",
    "#051c2c",  # highest value
]


@capture("graph")
def bar_chart_by_category(data_frame, custom_data):
    """Custom bar chart made with Plotly."""
    if not data_frame["Category"].eq(data_frame["Category"].iloc[0]).all():
        x = "Category"
    else:
        x = "Sub-Category"

    fig = px.bar(
        data_frame,
        x=x,
        y="Sales",
        title=f"Sales | By {x} <br><sup> 💡 Click on the category to drill-down to sub-category. "
        f"Reset by using reset button next to the theme switch.</sup>",
        custom_data=custom_data,
        color_discrete_sequence=[PRIMARY_COLOR],
    )

    fig.update_layout(
        yaxis={"visible": False},
        showlegend=False,
        bargap=0.6,
        xaxis_title=None,
        yaxis_title=None,
    )

    return fig


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
        color_continuous_scale=DIVERGING_RED_BLUE,
        color_continuous_midpoint=0,
    )

    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
    )
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "bottom"}, "orientation": "h", "x": 0.5, "y": 0})

    return fig


@capture("graph")
def create_lollipop_chart_by_region(data_frame, value_col="Sales"):
    """Create a lollipop chart showing aggregated metrics by region using Plotly."""
    # --- Aggregate based on chosen metric ---
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
        region_metric = (
            data_frame.groupby("Region", as_index=False)[value_col].sum().rename(columns={value_col: value_col})
        )
        agg_col = value_col

    # --- Sort regions for visual clarity ---
    region_metric = region_metric.sort_values(by=agg_col, ascending=True)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=region_metric[agg_col],
            y=region_metric["Region"],
            showlegend=False,
            hoverinfo="skip",
            orientation="h",
            marker={"color": PRIMARY_COLOR},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=region_metric[agg_col],
            y=region_metric["Region"],
            mode="markers",
            marker={"size": 14, "color": PRIMARY_COLOR, "line": {"color": PRIMARY_COLOR, "width": 1.5}},
            showlegend=False,
        )
    )

    fig.update_layout(
        title=f"{agg_col} | By Region",
        xaxis_title=None,
        yaxis_title=None,
        bargap=0.8,
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

    pivot_df = agg_df.pivot_table(index="Segment", columns="Year", values=agg_col).reset_index()

    fig = go.Figure()

    if PREVIOUS_YEAR in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[PREVIOUS_YEAR],
                name="Previous year",
                marker_color=SECONDARY_COLOR,
            )
        )

    if CURRENT_YEAR in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[CURRENT_YEAR],
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

    pivot_df = agg_df.pivot_table(index="Category", columns="Year", values=agg_col).reset_index()

    fig = go.Figure()

    if PREVIOUS_YEAR in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Category"],
                y=pivot_df[PREVIOUS_YEAR],
                name="Previous year",
                marker_color=SECONDARY_COLOR,
            )
        )

    if CURRENT_YEAR in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Category"],
                y=pivot_df[CURRENT_YEAR],
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

    prev_year = monthly[monthly["Year"] == PREVIOUS_YEAR]
    curr_year = monthly[monthly["Year"] == CURRENT_YEAR]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=curr_year["Month"],
            y=curr_year[agg_col],
            name="Current Year",
            marker_color=PRIMARY_COLOR,
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prev_year["Month"],
            y=prev_year[agg_col],
            name="Previous Year",
            marker_color=SECONDARY_COLOR,
        )
    )

    fig.update_layout(
        xaxis={
            "showgrid": False,
            "title": None,
            "tickmode": "array",
            "tickvals": list(range(1, 13)),
            "range": [1, 12],
            "ticktext": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        },
        yaxis_title=None,
        title=f"{agg_col} | By Month",
        legend={"yanchor": "top", "y": 1.2, "xanchor": "right", "x": 1},
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
        title=f"{agg_col} | By Order Status",
        legend={"yanchor": "bottom", "y": -0.2, "xanchor": "right", "orientation": "v"},
    )

    return fig


@capture("graph")
def scatter_with_quadrants(
    x: str,
    y: str,
    custom_data: list[str],
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
        color_discrete_sequence=[SECONDARY_COLOR],
        size="Profit Absolute",
        size_max=20,
        opacity=0.7,
        hover_data=["Sub-Category", "Profit", "Sales", "Profit Margin"],
        title="Profit vs. Sales by Sub-Category",
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
                marker={"color": ORANGE_COLOR, "size": marker_sizes, "line": {"width": 2, "color": "black"}},
                hovertext=highlight_sub_category,
                textposition="bottom center",
            )

    # Reference lines (based on all data)
    x_reference_line = data_frame[x].quantile(0.5)
    y_reference_line = data_frame[y].quantile(0.2)
    fig.add_hline(y=y_reference_line, line_dash="dash", line_color=SECONDARY_COLOR)
    fig.add_vline(x=x_reference_line, line_dash="dash", line_color=SECONDARY_COLOR)

    # Quadrant shading
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=x_reference_line,
        y0=data_frame[y].max() + 700,
        x1=data_frame[x].max() + 700,
        y1=y_reference_line,
        fillcolor=PRIMARY_COLOR,
        line_width=0,
        opacity=0.8,
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
        fillcolor=PRIMARY_COLOR,
        line_width=0,
        opacity=0.4,
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
        fillcolor=RED_COLOR,
        line_width=0,
        opacity=0.8,
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
        fillcolor=RED_COLOR,
        line_width=0,
        opacity=0.4,
        layer="below",
    )

    # Hover and legend tweaks
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

    fig.update_layout(
        title_pad_t=24,
        legend_title_text="Sub-Category",
        legend={"itemsizing": "trace", "orientation": "h", "yanchor": "bottom", "y": -0.3},
    )

    return fig


@capture("graph")
def pareto_customers_chart(data_frame, value_col="Sales", highlight_customer=None):
    """Custom chart made with Plotly."""
    customer_df = (
        data_frame.groupby("Customer Name", as_index=False)[value_col].sum().sort_values(by=value_col, ascending=False)
    )

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

    fig = px.line(
        customer_df,
        x="Cumulative % Customers",
        y="Cumulative % Value",
        markers=True,
        title=f"Pareto Analysis of Customers ({value_col})",
        hover_data=["Customer Name", value_col, "Cumulative % Value"],
        color_discrete_sequence=[ORANGE_COLOR],
    )
    fig.update_traces(showlegend=False)
    fig.add_vrect(x0=0, x1=thresholds["A"], fillcolor=PRIMARY_COLOR, opacity=0.6, layer="below")
    fig.add_vrect(x0=thresholds["A"], x1=thresholds["B"], fillcolor=PRIMARY_COLOR, opacity=0.3, layer="below")
    fig.add_vrect(x0=thresholds["B"], x1=100, fillcolor=PRIMARY_COLOR, opacity=0.1, layer="below")

    if highlight_customer and highlight_customer in customer_df["Customer Name"].to_numpy():
        cust = customer_df[customer_df["Customer Name"] == highlight_customer].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[cust["Cumulative % Customers"]],
                y=[cust["Cumulative % Value"]],
                mode="markers+text",
                text=[highlight_customer],
                textposition="top right",
                marker={"color": ORANGE_COLOR, "size": 12, "line": {"width": 2}},
                showlegend=False,
            )
        )

    fig.update_layout(
        xaxis_title="% of Total Customers",
        yaxis_title=f"Cumulative % of {value_col}",
        yaxis={"range": [0, 105]},
        xaxis={"range": [0, 105]},
    )

    return fig


CELL_STYLE_PRODUCT = {
    "styleConditions": [
        {
            "condition": "params.value < -0.5",
            "style": {"backgroundColor": "#e33b3b"},
        },
        {
            "condition": "params.value >= -0.5 && params.value <= 0",
            "style": {"backgroundColor": "#f19791"},
        },
        {
            "condition": "params.value > 0 && params.value <= 0.30",
            "style": {"backgroundColor": "#728aff"},
        },
        {
            "condition": "params.value > 0.30",
            "style": {"backgroundColor": "#2251ff"},
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


@capture("ag_grid")
def custom_orders_aggrid(data_frame):
    """Custom aggrid table."""
    data_frame["Profit Ratio"] = (data_frame["Profit"] / data_frame["Sales"]).round(3)
    column_defs_orders = [
        {"headerName": "Order ID", "field": "Order ID", "minWidth": 150},
        {"headerName": "Status", "field": "Order Status", "minWidth": 150, "cellRenderer": "statusCellRenderer"},
        {
            "headerName": "Segment",
            "field": "Segment",
            "minWidth": 140,
        },
        {"headerName": "Customer", "field": "Customer Name", "minWidth": 170},
        {"headerName": "State", "field": "State", "minWidth": 150},
        {"headerName": "City", "field": "City", "minWidth": 150},
        {"headerName": "Category", "field": "Category", "minWidth": 150},
        {"headerName": "Sub-Category", "field": "Sub-Category", "minWidth": 150},
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
                        "condition": "Number(params.value) < -0.5",
                        "style": {
                            "backgroundColor": "#e33b3b",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "30px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= -0.5 && Number(params.value) < 0",
                        "style": {
                            "backgroundColor": "#f19791",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "30px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0 && Number(params.value) < 0.30",
                        "style": {
                            "backgroundColor": "#728aff",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "30px",
                        },
                    },
                    {
                        "condition": "Number(params.value) >= 0.30",
                        "style": {
                            "backgroundColor": "#2251ff",
                            "color": "white",
                            "borderRadius": "18px",
                            "padding": "4px",
                            "fontWeight": "600",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "display": "flex",
                            "marginTop": "8px",
                            "height": "30px",
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
