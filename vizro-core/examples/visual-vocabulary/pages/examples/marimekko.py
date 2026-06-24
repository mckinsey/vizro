import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def marimekko(data_frame: pd.DataFrame, category: str, subcategory: str, values: str):
    totals = data_frame.groupby(category)[values].sum()
    categories = totals.index.tolist()
    widths = totals.to_numpy() / totals.to_numpy().sum()

    pct = data_frame.groupby(category)[values].transform(lambda x: x / x.sum() * 100)

    x_pos = []
    cumulative = 0
    for w in widths:
        x_pos.append(cumulative + w / 2)
        cumulative += w

    fig = go.Figure()
    customdata = [[cat, totals[cat]] for cat in categories]
    for sub in data_frame[subcategory].unique():
        sub_data = data_frame[data_frame[subcategory] == sub].copy()
        sub_data["pct"] = pct
        y_vals = []
        for cat in categories:
            match = sub_data[sub_data[category] == cat]
            y_vals.append(match["pct"].to_numpy()[0] if not match.empty else 0)

        fig.add_trace(
            go.Bar(
                x=x_pos,
                y=y_vals,
                width=widths,
                name=sub,
                customdata=customdata,
                text=[f"{v:.0f}%" if v > 15 else "" for v in y_vals],  # noqa: PLR2004
                textposition="inside",
                marker_line_width=1.5,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>%{data.name}: %{y:.1f}%<br>Total: %{customdata[1]}<extra></extra>"
                ),
            )
        )

    for xp, total in zip(x_pos, totals):
        fig.add_annotation(
            x=xp,
            y=112,
            text=str(total),
            showarrow=False,
            font_size=16,
        )

    fig.update_layout(
        barmode="stack",
        bargap=0,
        xaxis={
            "tickvals": x_pos,
            "ticktext": [f"<b>{cat}</b><br>{totals[cat]:.0f}" for cat in categories],
            "range": [0, 1],
            "showline": False,
            "showticklabels": False,
        },
        yaxis={
            "range": [0, 115],
            "showline": False,
            "showticklabels": False,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    return fig


marimekko_data = pd.DataFrame(
    {
        "Region": ["Europe", "Europe", "Europe", "Asia", "Asia", "Asia", "Americas", "Americas", "Americas"],
        "Segment": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
        "Value": [120, 200, 80, 150, 120, 80, 80, 110, 60],
    }
)

fig = marimekko(marimekko_data, category="Region", subcategory="Segment", values="Value")
