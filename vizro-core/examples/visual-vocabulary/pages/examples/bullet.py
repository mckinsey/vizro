"""Bullet chart for displaying actual values against targets with qualitative ranges."""

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture
from vizro.themes._palettes import qualitative

RANGE_BOUNDARIES = [0, 0.4, 0.75, 1.0]
RANGE_LABELS = ["Below average", "Average", "Above average"]
SCALE_HEADROOM = 1.4
TARGET_MARKER_SIZE = 28
TARGET_MARKER_LINE_WIDTH = 5


@capture("graph")
def bullet(data_frame: pd.DataFrame, category: str, actual: str, target: str) -> go.Figure:
    """Creates a bullet chart comparing actual performance against targets over qualitative ranges."""
    fig = go.Figure()

    categories = data_frame[category].tolist()
    actual_values = data_frame[actual].tolist()
    target_values = data_frame[target].tolist()

    max_val = max(max(actual_values), max(target_values), 0.0)
    max_scale = max(max_val * SCALE_HEADROOM, 1.0)
    colorway = fig.layout.template.layout.colorway

    prev = 0
    range_opacities = [0.3, 0.45, 0.3]
    for i, boundary in enumerate(RANGE_BOUNDARIES[1:]):
        width = boundary * max_scale - prev
        fig.add_trace(
            go.Bar(
                y=categories,
                x=[width] * len(categories),
                base=[prev] * len(categories),
                orientation="h",
                marker={"color": qualitative[i + 1], "opacity": range_opacities[i]},
                name=RANGE_LABELS[i],
                legendrank=i + 3,
                hoverinfo="text",
                hovertext=[
                    f"<b>{c}</b><br>{RANGE_LABELS[i]}: {prev:.1f}–{boundary * max_scale:.1f}" for c in categories
                ],
            )
        )
        prev = boundary * max_scale

    fig.add_trace(
        go.Bar(
            y=categories,
            x=actual_values,
            orientation="h",
            marker={"color": colorway[0]},
            name="Actual",
            legendrank=1,
            hoverinfo="text",
            hovertext=[f"<b>{c}</b><br>Actual: {v}" for c, v in zip(categories, actual_values)],
        )
    )

    fig.add_trace(
        go.Scatter(
            y=categories,
            x=target_values,
            mode="markers",
            marker={
                "symbol": "line-ns",
                "size": TARGET_MARKER_SIZE,
                "color": colorway[0],
                "line": {"width": TARGET_MARKER_LINE_WIDTH, "color": colorway[0]},
            },
            name="Target",
            legendrank=2,
            hoverinfo="text",
            hovertext=[f"<b>{c}</b><br>Target: {v}" for c, v in zip(categories, target_values)],
        )
    )

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(range=[0, max_scale * 1.08], showgrid=True, zeroline=False),
        yaxis=dict(showgrid=False),
        margin=dict(b=50),
    )

    return fig


data = pd.DataFrame(
    {
        "metric": ["Revenue", "Profit", "Customer satisfaction"],
        "actual": [8.5, 5.2, 7.8],
        "target": [9.0, 6.0, 8.5],
    }
)

fig = bullet(data, category="metric", actual="actual", target="target")
