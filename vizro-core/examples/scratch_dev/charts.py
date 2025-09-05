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
        yaxis_title="",
        xaxis_title="",
        barmode="stack",
        legend_title=None,
    )
    fig.update_xaxes(tickfont=dict(size=13), minor_tickwidth=2, ticklen=2, tickangle=10)

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


@capture("graph")
def custom_waterfall_chart(data_frame):
    """Creates a waterfall chart similar to the provided image."""
    # Prepare data for waterfall chart
    categories = data_frame["Category"].tolist()
    values = data_frame["Value"].tolist()

    # Calculate cumulative values for positioning
    cumulative = []
    running_total = 0

    for i, value in enumerate(values):
        if i == 0:  # First bar starts from 0
            cumulative.append(0)
            running_total = value
        elif i == len(values) - 1:  # Last bar (total) starts from 0
            cumulative.append(0)
        else:  # Intermediate bars start from previous cumulative
            cumulative.append(running_total)
            running_total += value

    # Create the waterfall chart
    fig = go.Figure()

    # Define colors for different types of bars
    colors = []
    for i, (cat, val) in enumerate(zip(categories, values)):
        if i == 0:  # Current (base)
            colors.append("#1f77b4")  # Blue
        elif i == len(categories) - 1:  # Total
            colors.append("#d62728")  # Light gray/white for total
        elif val > 0:  # Positive contributions
            colors.append("#2ca02c" if "Cross" in cat or "Pricing" in cat else "#17becf")  # Green/teal for positive
        else:  # Negative contributions (Churn)
            colors.append("#ff7f0e")  # Orange for negative

    # Add bars
    fig.add_trace(
        go.Waterfall(
            name="",
            orientation="v",
            measure=["absolute"] + ["relative"] * (len(categories) - 2) + ["total"],
            x=categories,
            y=values,
            text=[f"{val}M" for val in values],
            textposition="outside",
            textfont=dict(color="white", size=14),
            connector={"line": {"color": "rgba(255,255,255,0.3)", "width": 1}},
            increasing={"marker": {"color": "#17becf"}},
            decreasing={"marker": {"color": "#ff7f0e"}},
            totals={"marker": {"color": "#d62728"}},
            base=0,
        )
    )

    # Update layout to match the dark theme from the image
    fig.update_layout(
        plot_bgcolor="#2e2e2e",
        paper_bgcolor="#2e2e2e",
        font=dict(color="white", family="Arial", size=12),
        xaxis=dict(title="", showgrid=False, showline=False, zeroline=False, tickfont=dict(color="white", size=12)),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
            showline=False,
            zeroline=False,
            ticksuffix="M",
            tickfont=dict(color="white", size=12),
            range=[0, max(values) * 1.2],
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig
