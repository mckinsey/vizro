import math

import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


def _create_arc_path(
    x1: float,
    x2: float,
    baseline_y: float = 0.0,
    num_points: int = 80,
) -> tuple:
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
    node_indices = {node: idx for idx, node in enumerate(unique_nodes)}
    node_positions = {node: i * spacing for i, node in enumerate(unique_nodes)}

    node_x = [node_positions[n] for n in unique_nodes]
    baseline_y = 0.0
    node_y = [baseline_y] * num_nodes

    colors = [
        "rgba(93, 156, 236, 0.75)",
        "rgba(172, 146, 236, 0.75)",
        "rgba(72, 207, 173, 0.75)",
        "rgba(236, 135, 192, 0.75)",
        "rgba(252, 110, 81, 0.75)",
        "rgba(255, 206, 84, 0.75)",
        "rgba(160, 212, 104, 0.75)",
        "rgba(79, 193, 233, 0.75)",
    ]
    edge_colors = colors * 3

    fig = go.Figure()
    max_arc_height = 0

    max_value = 1
    if value and value in data_frame.columns:
        max_value = max(data_frame[value].max(), 1)

    edges_with_info = []
    for idx, (_, row) in enumerate(data_frame.iterrows()):
        src, tgt = row[source], row[target]
        if src not in node_positions or tgt not in node_positions:
            continue
        x1, x2 = node_positions[src], node_positions[tgt]
        distance = abs(x2 - x1)
        source_idx = node_indices[src]
        target_idx = node_indices[tgt]
        edges_with_info.append((idx, src, tgt, row, distance, source_idx, target_idx))

    edges_with_info.sort(key=lambda x: (x[4], x[5]))
    for draw_order, (idx, src, tgt, row, distance, source_idx, target_idx) in enumerate(edges_with_info):
        x1, x2 = node_positions[src], node_positions[tgt]
        path_x, path_y = _create_arc_path(x1, x2, baseline_y=baseline_y)
        max_arc_height = max(max_arc_height, max(path_y, default=0))

        weight = row[value] if value and value in row and pd.notna(row[value]) else 1
        line_width = 1.5 + (weight / max_value) * 1.8

        color = edge_colors[draw_order % len(edge_colors)]
        fig.add_trace(
            go.Scatter(
                x=path_x,
                y=path_y,
                mode="lines",
                line={"color": color, "width": line_width},
                hoverinfo="text",
                hovertext=f"{src} → {tgt}<br>Weight: {weight}",
                showlegend=False,
            )
        )

    node_size = max(15, 22 - num_nodes * 0.5)
    connection_counts = {
        node: ((data_frame[source] == node) | (data_frame[target] == node)).sum()
        for node in unique_nodes
    }
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker={"size": node_size, "color": "#34495E", "line": {"color": "#34495E", "width": 0.6}, "opacity": 0.98},
            text=unique_nodes,
            textposition="bottom center",
            textfont={"size": 12, "color": "#2C3E50"},
            texttemplate="<b>%{text}</b>",
            hoverinfo="text",
            hovertext=[f"<b>{n}</b><br>Connections: {connection_counts[n]}" for n in unique_nodes],
        )
    )

    upper_extent = max(max_arc_height, max(node_y, default=0))
    upper_padding = max(0.35, upper_extent * 0.12)
    lower_padding = max(0.55, node_size * 0.05)
    x_range = [
        min(node_x, default=0) - horizontal_padding,
        max(node_x, default=0) + horizontal_padding,
    ]
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        autosize=True,
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": x_range,
        },
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "range": [-lower_padding, upper_extent + upper_padding],
        },
        margin={"l": 40, "r": 40, "t": 40, "b": 40},
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
