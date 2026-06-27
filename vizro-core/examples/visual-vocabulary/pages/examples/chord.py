import math

import pandas as pd
import plotly.graph_objects as go
from pycirclize import Circos
from pycirclize.parser import Matrix
from vizro.models.types import capture

COLORS = ["#497DEF", "#6F39E3", "#05D0E0", "#0F766E", "#E77EC2"]
NODES = ["USA", "China", "EU", "Japan", "India"]
R = 1.4
ARC_WIDTH = 0.06
INNER_R = R - ARC_WIDTH
GAP_DEG = 5

flow_matrix = [
    [0, 150, 100, 30, 20],
    [80, 0, 120, 40, 20],
    [70, 130, 0, 20, 15],
    [25, 35, 30, 0, 5],
    [15, 25, 20, 10, 0],
]
flows_data = pd.DataFrame(flow_matrix, index=NODES, columns=NODES)


def _point(angle, radius=R):
    return radius * math.cos(angle), radius * math.sin(angle)


def _arc_points(angle_start, angle_end, n=40, radius=R):
    xs, ys = [], []
    for i in range(n + 1):
        t = i / n
        a = angle_start + t * (angle_end - angle_start)
        x, y = _point(a, radius)
        xs.append(x)
        ys.append(y)
    return xs, ys


def _arc_ring(angle_start, angle_end, n=40):
    outer_x, outer_y = _arc_points(angle_start, angle_end, n, R)
    inner_x, inner_y = _arc_points(angle_end, angle_start, n, INNER_R)
    return outer_x + inner_x, outer_y + inner_y


def _bezier_quad(rad_a, rad_b, r_a, r_b, n=20):
    ctrl_x = 0.0
    ctrl_y = 0.0
    x1, y1 = r_a * math.cos(rad_a), r_a * math.sin(rad_a)
    x2, y2 = r_b * math.cos(rad_b), r_b * math.sin(rad_b)
    xs, ys = [], []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u * u * x1 + 2 * u * t * ctrl_x + t * t * x2
        y = u * u * y1 + 2 * u * t * ctrl_y + t * t * y2
        xs.append(x)
        ys.append(y)
    return xs, ys


def _ribbon_polygon(rad_src_start, rad_src_end, rad_tgt_start, rad_tgt_end, n=20):
    src_x, src_y = _arc_points(rad_src_start, rad_src_end, n, INNER_R)
    tgt_x, tgt_y = _arc_points(rad_tgt_end, rad_tgt_start, n, INNER_R)
    out_bx, out_by = _bezier_quad(rad_src_end, rad_tgt_end, INNER_R, INNER_R, n)
    in_bx, in_by = _bezier_quad(rad_tgt_start, rad_src_start, INNER_R, INNER_R, n)
    xs = src_x + out_bx + tgt_x + in_bx
    ys = src_y + out_by + tgt_y + in_by
    return xs, ys


@capture("graph")
def chord_diagram(data_frame, node_labels):
    if len(node_labels) > len(COLORS):
        raise ValueError(f"Only {len(COLORS)} colors defined but {len(node_labels)} nodes provided")
    matrix = Matrix(data_frame)

    circos = Circos(matrix.to_sectors(), space=GAP_DEG)

    sector_names = [s.name for s in circos.sectors]
    sector_start_rad = {}
    sector_end_rad = {}
    for s in circos.sectors:
        sector_start_rad[s.name] = s.x_to_rad(s.start)
        sector_end_rad[s.name] = s.x_to_rad(s.end)

    links = matrix.to_links()

    fig = go.Figure()

    for link in links:
        (name1, start1, end1), (name2, start2, end2) = link
        sector1 = circos.get_sector(name1)
        sector2 = circos.get_sector(name2)

        rad_src_start = sector1.x_to_rad(start1)
        rad_src_end = sector1.x_to_rad(end1)
        rad_tgt_start = sector2.x_to_rad(start2)
        rad_tgt_end = sector2.x_to_rad(end2)

        src_idx = node_labels.index(name1) if name1 in node_labels else 0

        xs, ys = _ribbon_polygon(rad_src_start, rad_src_end, rad_tgt_start, rad_tgt_end)

        val = int(data_frame.loc[name1, name2])

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                fill="toself",
                mode="lines",
                line={"width": 0},
                fillcolor=COLORS[src_idx],
                opacity=0.35,
                showlegend=False,
                hoverinfo="skip",
            )
        )

        src_mid = (rad_src_start + rad_src_end) / 2
        tgt_mid = (rad_tgt_start + rad_tgt_end) / 2
        hx, hy = _bezier_quad(src_mid, tgt_mid, INNER_R, INNER_R, n=10)
        fig.add_trace(
            go.Scatter(
                x=hx,
                y=hy,
                mode="markers",
                marker={"size": 10, "opacity": 0.01, "color": COLORS[src_idx]},
                showlegend=False,
                hovertemplate=f"{name1} -&gt; {name2}<br>Flow: {val}<extra></extra>",
            )
        )

    for i, name in enumerate(sector_names):
        rx, ry = _arc_ring(sector_start_rad[name], sector_end_rad[name])
        fig.add_trace(
            go.Scatter(
                x=rx,
                y=ry,
                fill="toself",
                mode="lines",
                line={"width": 0},
                fillcolor=COLORS[i],
                showlegend=False,
                hoverinfo="none",
            )
        )

    circle_x, circle_y = _arc_points(0, 2 * math.pi, 60, R)
    fig.add_trace(
        go.Scatter(
            x=circle_x,
            y=circle_y,
            mode="lines",
            line={"color": "rgba(128,128,128,0.3)", "width": 1},
            showlegend=False,
            hoverinfo="none",
        )
    )

    label_angles = [(sector_start_rad[name] + sector_end_rad[name]) / 2 for name in sector_names]
    label_r = 1.6
    label_x = [label_r * math.cos(a) for a in label_angles]
    label_y = [label_r * math.sin(a) for a in label_angles]
    fig.add_trace(
        go.Scatter(
            x=label_x,
            y=label_y,
            mode="text",
            text=sector_names,
            textfont={"size": 14},
            showlegend=False,
            hoverinfo="none",
        )
    )

    fig.update_layout(
        xaxis={"visible": False, "range": [-1.85, 1.85]},
        yaxis={"visible": False, "range": [-1.85, 1.85], "scaleanchor": "x"},
        showlegend=False,
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
    )
    return fig


fig = chord_diagram(flows_data, node_labels=NODES)
