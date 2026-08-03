import math

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture
from vizro.themes._colors import colors
from vizro.themes._palettes import qualitative


def _create_arc_path(
    x1: float,
    x2: float,
    baseline_y: float = 0.0,
    num_points: int = 80,
) -> tuple[list[float], list[float]]:
    """Create a classic upper semicircle between two baseline points."""
    left_x = min(x1, x2)
    right_x = max(x1, x2)
    radius = (right_x - left_x) / 2
    if radius <= 0:
        return [x1, x2], [baseline_y, baseline_y]
    center_x = (left_x + right_x) / 2
    path_x = []
    path_y = []
    for i in range(num_points + 1):
        t = i / num_points
        theta = math.pi * (1 - t)
        x = center_x + radius * math.cos(theta)
        y = baseline_y + radius * math.sin(theta)
        path_x.append(x)
        path_y.append(y)
    if x1 > x2:
        path_x.reverse()
        path_y.reverse()
    return path_x, path_y


@capture("graph")
def arc(data_frame: pd.DataFrame, source: str, target: str, value: str | None = None) -> go.Figure:
    """Create a polished arc diagram with nodes on a horizontal line and curved arcs."""
    unique_nodes = list(set(data_frame[source].unique()) | set(data_frame[target].unique()))
    unique_nodes.sort()
    num_nodes = len(unique_nodes)

    spacing = 1.2
    horizontal_padding = max(0.45, spacing * 0.5)
    node_positions = {node: i * spacing for i, node in enumerate(unique_nodes)}

    node_x = [node_positions[n] for n in unique_nodes]
    baseline_y = 0.0
    node_y = [baseline_y] * num_nodes

    fig = go.Figure()
    max_arc_height = 0

    max_value = 1
    if value and value in data_frame.columns:
        max_value = max(data_frame[value].max(), 1)

    edges_with_info = []
    for _, row in data_frame.iterrows():
        src, tgt = row[source], row[target]
        if src not in node_positions or tgt not in node_positions:
            continue
        x1, x2 = node_positions[src], node_positions[tgt]
        distance = abs(x2 - x1)
        edges_with_info.append((src, tgt, row, distance))

    edges_with_info.sort(key=lambda x: x[3])
    for draw_order, (src, tgt, row, _distance) in enumerate(edges_with_info):
        x1, x2 = node_positions[src], node_positions[tgt]
        path_x, path_y = _create_arc_path(x1, x2, baseline_y=baseline_y)
        max_arc_height = max(max_arc_height, max(path_y, default=0))

        weight = row[value] if value and value in row and pd.notna(row[value]) else 1
        line_width = 1.5 + (weight / max_value) * 1.8

        fig.add_trace(
            go.Scatter(
                x=path_x,
                y=path_y,
                mode="lines",
                line={"color": qualitative[draw_order % len(qualitative)], "width": line_width},
                hoverinfo="text",
                hovertext=f"{src} → {tgt}<br>Weight: {weight}",
                showlegend=False,
            )
        )

    node_size = max(15, 22 - num_nodes * 0.5)
    connection_counts = {
        node: ((data_frame[source] == node) | (data_frame[target] == node)).sum() for node in unique_nodes
    }
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker={"size": node_size, "color": colors.gray_700},
            text=unique_nodes,
            textposition="bottom center",
            textfont={"size": 12},
            texttemplate="<b>%{text}</b>",
            hoverinfo="text",
            hovertext=[f"<b>{n}</b><br>Connections: {connection_counts[n]}" for n in unique_nodes],
        )
    )

    upper_extent = max(max_arc_height, max(node_y, default=0))
    lower_padding = 0.2
    upper_padding = max(0.25, upper_extent * 0.15)

    x_range = [
        min(node_x, default=0) - horizontal_padding,
        max(node_x, default=0) + horizontal_padding,
    ]

    fig.update_layout(
        showlegend=False,
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": x_range,
            "constrain": "domain",
        },
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": [-lower_padding, upper_extent + upper_padding],
            "scaleanchor": "x",
            "scaleratio": 1,
        },
        margin={"l": 30, "r": 30, "t": 20, "b": 45},
    )

    return fig


arc_data = pd.DataFrame(
    {
        "source": ["A", "B", "C", "D", "E", "A", "B", "C", "D"],
        "target": ["B", "C", "D", "E", "C", "D", "E", "D", "E"],
        "value": [10, 20, 15, 25, 8, 12, 18, 22, 16],
    }
)

fig = arc(arc_data, source="source", target="target", value="value")
