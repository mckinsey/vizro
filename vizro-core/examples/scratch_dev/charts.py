"""Collection of custom charts."""

# import plotly.express as px
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro.models.types import capture
import pandas as pd


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
        x="Segment",
        y=value_col,
        color="Segment",
        title=f"{value_col} | By Segment",
        custom_data=custom_data,
    )

    fig.update_layout(title=dict(x=0.5, xanchor="center"), yaxis=dict(visible=False), showlegend=False)
    fig.update_layout(bargap=0.6, xaxis_title=None, yaxis_title=None)
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
def bar_chart_sales_by_customer(data_frame, custom_data, value_col="Sales"):
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
        custom_data=custom_data,
    )

    fig.update_layout(
        title=f"<b>{value_col}</b> | By Top 10 Customers",
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