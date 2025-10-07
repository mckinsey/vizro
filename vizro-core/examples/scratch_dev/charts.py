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
        hole=0.6,  # optional: makes it a donut chart
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
    if value_col == "Order ID":
        category_metric = data_frame.groupby("Category", as_index=False)["Order ID"].nunique()
        agg_col = "Order ID"
    else:
        category_metric = data_frame.groupby("Category", as_index=False)[value_col].sum()
        agg_col = value_col

    fig = px.bar(
        category_metric,
        x="Category",
        y=agg_col,
        title=f"{agg_col} | By Category",
        color="Category",
        custom_data=custom_data,
    )

    fig.update_layout(
        yaxis=dict(visible=False),
        showlegend=False,
        bargap=0.6,
        xaxis_title=None,
        yaxis_title=None,
        title=dict(
            text=f"{agg_col} | By Category",
        ),
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
        color_discrete_sequence=["#4dabf7"] + ["#ff9222"] * 9,
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
    if value_col == "Order ID":
        state_metric = data_frame.groupby(["State_Code", "Region"], as_index=False)["Order ID"].nunique()
        agg_col = "Order ID"
    else:
        state_metric = data_frame.groupby(["State_Code", "Region"], as_index=False)[value_col].sum()
        agg_col = value_col

    # Choropleth
    fig = px.choropleth(
        state_metric,
        locations="State_Code",
        locationmode="USA-states",
        color=value_col,
        hover_name="Region",
        hover_data=["Region", agg_col],
        scope="usa",
        custom_data=custom_data,
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "bottom"}, "orientation": "h", "x": 0.5, "y": 0})

    return fig


@capture("graph")
def create_bar_chart_by_region(data_frame, value_col="Sales", highlight_region=None):
    if value_col == "Order ID":
        region_metric = (
            data_frame.groupby("Region", as_index=False)["Order ID"].nunique().rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    else:
        region_metric = data_frame.groupby("Region", as_index=False)[value_col].sum()
        agg_col = value_col

    fig = px.bar(
        region_metric,
        y="Region",
        x=agg_col,
        orientation="h",
    )

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
    data_frame["YearMonth"] = data_frame["Order Date"].dt.to_period("M").astype(str)
    monthly_sales = data_frame.groupby("YearMonth", as_index=False)["Sales"].sum()

    fig = px.line(
        monthly_sales,
        x="YearMonth",
        y="Sales",
        markers=True,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


@capture("graph")
def create_bar_current_vs_previous_segment(data_frame, value_col="Sales"):
    data_frame["Order Date"] = pd.to_datetime(data_frame["Order Date"])
    data_frame["Year"] = data_frame["Order Date"].dt.year

    if value_col == "Order ID":
        agg_df = (
            data_frame.groupby(["Segment", "Year"], as_index=False)["Order ID"]
            .nunique()
            .rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
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
            )
        )

    if 2017 in pivot_df.columns:
        fig.add_trace(
            go.Bar(
                x=pivot_df["Segment"],
                y=pivot_df[2017],
                name="Current year",
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title=None,
        yaxis_title=agg_col,
        bargap=0.25,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    return fig


@capture("graph")
def create_line_chart_sales_profit_per_month(data_frame):
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
    else:
        monthly = data_frame.groupby(["Year", "Month"], as_index=False)[value_col].sum()
        agg_col = value_col

    prev_year = monthly[monthly["Year"] == 2016]
    curr_year = monthly[monthly["Year"] == 2017]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=prev_year["Month"], y=prev_year[agg_col], mode="lines+markers", name="Previous Year"))
    fig.add_trace(go.Scatter(x=curr_year["Month"], y=curr_year[agg_col], mode="lines+markers", name="Current Year"))

    fig.update_layout(
        title=f"{agg_col} per Month: Current Year vs Previous Year",
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        ),
        yaxis_title=agg_col,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_layout(
        title={
            "text": f"{agg_col} per Month: Current Year vs Previous Year",
            "y": 1,
            "yanchor": "top",
        },
        title_pad=dict(t=10),
    )

    return fig


@capture("graph")
def pareto_customers_chart(data_frame, custom_data, highlight_customer=None):
    customer_sales = data_frame.groupby("Customer Name")["Sales"].sum().reset_index()

    customer_sales = customer_sales.sort_values(by="Sales", ascending=False)

    customer_sales["Cumulative Sales"] = customer_sales["Sales"].cumsum()
    customer_sales["Cumulative %"] = 100 * customer_sales["Cumulative Sales"] / customer_sales["Sales"].sum()

    customer_sales["Rank"] = range(1, len(customer_sales) + 1)

    fig = px.bar(
        customer_sales,
        x="Rank",
        y="Sales",
        hover_data=["Customer Name"],
        labels={"Sales": "Sales ($)", "Rank": "Customer Rank"},
        title="Pareto Analysis of Customers",
        custom_data=custom_data,
        color="Customer Name",
        color_discrete_sequence=["#4dabf7"],
    )

    fig.add_scatter(
        x=customer_sales["Rank"],
        y=customer_sales["Cumulative %"],
        mode="lines+markers",
        name="Cumulative %",
        yaxis="y2",
    )

    fig.update_layout(
        yaxis=dict(title="Sales ($)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 110]),
        bargap=0.1,
        showlegend=False,
    )

    if highlight_customer:
        for trace in fig.data:
            if trace.name == highlight_customer:
                trace.opacity = 1
                trace.marker.color = "orange"
            else:
                trace.opacity = 0.2

    return fig


@capture("graph")
def create_top_10_states(data_frame, value_col="Sales"):
    state_sales = data_frame.groupby(["State"], as_index=False)["Sales"].sum()
    state_sales["Rank"] = state_sales.groupby("State")["Sales"].rank(method="first", ascending=False)

    top_states = state_sales[state_sales["Rank"] <= 10]

    fig = px.bar(
        top_states,
        x=value_col,
        y="State",
        # color="Region",
        orientation="h",
        title=f"Top 10 States by {value_col}",
    )

    fig.update_yaxes(categoryorder="total ascending")
    return fig


@capture("graph")
def pie_chart_by_region(data_frame, value_col="Sales"):
    fig = px.pie(
        data_frame,
        names="Region",
        values=value_col,
        color="Region",
        title=f"{value_col} | By Region",
        hole=0.6,
    )

    fig.update_layout(title=dict(x=0.5, xanchor="center"))
    return fig


@capture("graph")
def bar_chart_by_state(data_frame, value_col="Sales"):
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
def pie_chart_by_category(data_frame, value_col="Sales"):
    if value_col == "Order ID":
        category_metric = (
            data_frame.groupby("Category", as_index=False)["Order ID"].nunique().rename(columns={"Order ID": "Orders"})
        )
        agg_col = "Orders"
    else:
        category_metric = data_frame.groupby("Category", as_index=False)[value_col].sum()
        agg_col = value_col

    fig = px.pie(
        category_metric,
        names="Category",
        values=agg_col,
        color="Category",
        title=f"{agg_col} | By Category",
        hole=0.6,
    )

    fig.update_layout(
        title=dict(
            text=f"{agg_col} | By Category",
        ),
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
):
    """Custom scatter plot with quadrants made with Plotly."""
    fig = px.scatter(
        data_frame=data_frame,
        x=x,
        y=y,
        custom_data=custom_data,
        color_discrete_sequence=["grey"],
        size="Profit Absolute",
        size_max=20,
        opacity=0.6,
        hover_data=["Product Name", "Profit", "Sales", "Profit Margin"],
        title=f"{data_frame['Category / Sub-Category'].iloc[0]} <br><sup> ⤵ Click on a point to filter the table. Refresh the page to deselect.</sup>",
    )

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
        hovertemplate="<br>".join(
            [
                "%{customdata[0]}",
                "Profit: %{y:$,.2f}",
                "Sales: %{x:$,.2f}",
            ]
        )
        + "<extra></extra>"
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
    {"field": "Product Name", "cellDataType": "text", "headerName": "Product", "flex": 3},
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
    df_sorted = data_frame.sort_values(value_col, ascending=True)
    fig = px.bar(
        df_sorted,
        x="Category",
        y=value_col,
        title=f"{value_col} | By Category",
        custom_data=custom_data,
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(bargap=0.6, xaxis_title=None, yaxis_title=None)

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
        "field": "Cumulative Sales",
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
