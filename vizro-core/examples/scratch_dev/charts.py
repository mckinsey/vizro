"""Collection of custom charts."""

import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def custom_market_industry_bar_chart(data_frame, custom_data=[]):
    """Creates custom bar chart."""
    # Reshape data to long format
    df_long = data_frame.melt(
        id_vars=["Industry", "Total"], value_vars=["2024_Revenue", "Opportunity"], var_name="Type", value_name="Value"
    )

    # Create stacked horizontal bar chart
    fig = px.bar(
        df_long,
        x="Value",
        y="Industry",
        color="Type",
        orientation="h",
        text=df_long["Value"].astype(str) + "M",
        custom_data=custom_data,
        labels={"2024_Revenue": "2024"},
    )

    # Add total labels as annotations
    for i, row in data_frame.iterrows():
        fig.add_annotation(
            x=row["Total"] + 2,
            y=row["Industry"],
            text=f"{row['Total']}M",
            showarrow=False,
            xanchor="left",
        )

    # Layout tweaks
    fig.update_traces(textposition="inside")
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="", showgrid=False, zeroline=False),
        yaxis=dict(title="", categoryorder="total ascending"),
        font=dict(color="white"),
        legend_title=None,
    )

    return fig


@capture("graph")
def custom_map_chart(data_frame):
    """Creates custom map chart."""
    fig = px.choropleth(
        data_frame,
        locations="state",
        color="market_numeric",
        locationmode="USA-states",
        scope="usa",
        hover_name="state",
        hover_data={"market_level": True, "market_numeric": False},
        labels={"market_numeric": "Market Level", "market_level": "Market Level"},
        center={"lat": 37.0902, "lon": -95.7129},
    )

    fig.update_layout(
        font=dict(color="white", family="Arial"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_layout(geo=dict(projection_scale=1.15))

    fig.update_traces(
        marker_line_color="white",
        marker_line_width=0.5,
        hovertemplate="<b>%{hovertext}</b><br>Market Level: %{customdata[0]}<extra></extra>",
    )

    # Add custom legend
    legend_colors = ["#143771", "#408CCB", "#BBE5F7"]
    legend_labels = ["High", "Medium", "Low"]

    for i, (color, label) in enumerate(zip(legend_colors, legend_labels)):
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode="markers", marker=dict(size=10, color=color), showlegend=True, name=label
            )
        )
    fig.update_layout(
        legend=dict(
            orientation="v",
            x=1.05,
            y=0.5,
            font=dict(color="white"),
            xanchor="left",
            yanchor="bottom",
        )
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return fig


def insert_br_every_n_chars(text, n=8):
    """Inserts <br> every n characters in the given text.

    Args:
        text (str): The input string.
        n (int): Number of characters between <br> tags. Default is 15.

    Returns:
        str: String with <br> inserted.
    """
    # Split the string into chunks of size n and join with <br>
    return "<br>".join(text[i : i + n] for i in range(0, len(text), n))


@capture("graph")
def custom_market_category_bar_chart(data_frame, custom_data=[]):
    """Creates custom bar chart."""
    fig = px.bar(data_frame, x="Category", y="Value", color="Type", text="Value", custom_data=custom_data)
    x_axis_values = []
    for value in list(data_frame["Category"]):
        x_axis_values.append(insert_br_every_n_chars(value))

    fig.update_layout(
        title="Serviceable Addressable Market by Product Category",
        yaxis_title="",
        xaxis_title="",
        barmode="stack",
        font=dict(color="white", size=8),
        legend_title=None,
    )
    fig.update_xaxes(tickfont=dict(size=9), minor_tickwidth=2, ticklen=2, tickangle=10)

    return fig


@capture("graph")
def custom_market_summary_bar_chart(data_frame):
    """Creates custom bar chart."""
    categories = [
        "Protein<br>Solutions",
        "Emulsifiers<br>& Sweeteners",
        "Cellulosics<br>& Food Protection",
        "Core<br>Texturants",
        "Systems",
        "Savory<br>Solutions",
        "Inclusions",
    ]
    totals = data_frame.groupby("Category", sort=False)["Value"].sum().reindex(categories)

    component_order = ["Churn", "Cross-sell", "Current", "Pricing", "Whitespace"]

    fig = px.bar(
        data_frame,
        x="Category",
        y="Value",
        color="Component",
        text="Label",
        category_orders={"Category": categories, "Component": component_order},
    )

    fig.update_layout(barmode="stack", bargap=0.28, bargroupgap=0.05)

    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=16, color="white"),
        cliponaxis=False,
        hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>%{y}M<extra></extra>",
    )

    fig.add_trace(
        go.Scatter(
            x=totals.index.tolist(),
            y=(totals.values + 2).tolist(),
            mode="text",
            text=[f"{int(v)}M" for v in totals.values],
            textfont=dict(size=16, color="white"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        margin=dict(t=60, r=20, b=80, l=50),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.6,
            font=dict(size=14, color="white"),
            itemclick=False,
            itemdoubleclick=False,
        ),
        font=dict(color="white"),
    )

    fig.update_yaxes(
        range=[0, 85],
        dtick=10,
        ticksuffix="M",
        zeroline=False,
        showline=False,
        showgrid=True,
    )

    fig.update_xaxes(
        tickfont=dict(size=12),
        ticklabelposition="outside",
        tickangle=0,
        showgrid=False,
        showline=False,
    )
    return fig
