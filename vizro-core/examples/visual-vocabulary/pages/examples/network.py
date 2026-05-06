import math
from collections import deque

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture

COLORS = [
    "#3498db",
    "#e74c3c",
    "#2ecc71",
    "#9b59b6",
    "#f39c12",
    "#1abc9c",
    "#e67e22",
    "#34495e",
    "#95a5a6",
    "#d35400",
    "#8e44ad",
    "#27ae60",
    "#c0392b",
    "#16a085",
    "#f1c40f",
]


@capture("graph")
def network(data_frame: pd.DataFrame, source: str, target: str) -> go.Figure:
    G = nx.Graph()
    for s, t in zip(data_frame[source], data_frame[target]):
        G.add_edge(s, t)

    nodes = list(G.nodes())
    degree = dict(G.degree())
    hub = max(degree, key=degree.get)

    levels, parent = {hub: 0}, {hub: None}
    queue = deque([hub])
    while queue:
        current = queue.popleft()
        for n in G.neighbors(current):
            if n not in levels:
                levels[n] = levels[current] + 1
                parent[n] = current
                queue.append(n)

    pos, level1 = {}, [n for n in nodes if levels.get(n) == 1]
    sector = 2 * math.pi / len(level1)

    for i, n in enumerate(level1):
        pos[n] = (3 * math.cos(-math.pi / 2 + (i + 0.5) * sector), 3 * math.sin(-math.pi / 2 + (i + 0.5) * sector))

    def place(pnode, pangle, psec, lvl):
        children = [n for n in nodes if parent.get(n) == pnode]
        if not children:
            return
        sec = psec * 0.35
        for i, c in enumerate(children):
            ang = pangle + (i - (len(children) - 1) / 2) * (sec / max(1, len(children) - 1))
            pos[c] = (lvl * 3.5 * math.cos(ang), lvl * 3.5 * math.sin(ang))
            place(c, ang, sec, lvl + 1)

    for i, n in enumerate(level1):
        place(n, -math.pi / 2 + (i + 0.5) * sector, sector, 2)
    pos[hub] = (0, 0)

    node_x = [pos[n][0] for n in nodes]
    node_y = [pos[n][1] for n in nodes]

    min_d, max_d = min(degree.values()), max(degree.values())
    sizes = [15 + 20 * (degree[n] - min_d) / (max_d - min_d) if max_d > min_d else 18 for n in nodes]

    fig = go.Figure()
    edge_x, edge_y = [], []
    for e in G.edges():
        edge_x.extend([pos[e[0]][0], pos[e[1]][0], None])
        edge_y.extend([pos[e[0]][1], pos[e[1]][1], None])
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line={"width": 1.5, "color": "gray"}, hoverinfo="none"))
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker={"size": sizes, "color": COLORS, "line": {"color": "white", "width": 2}},
            text=nodes,
            textposition="top center",
            textfont={"size": 10, "color": "gray"},
            hoverinfo="text",
            hovertext=[f"{n}: {degree[n]}" for n in nodes],
        )
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    return fig


network_data = pd.DataFrame(
    {
        "source": [
            "CEO",
            "CEO",
            "CEO",
            "CTO",
            "CTO",
            "CFO",
            "CFO",
            "COO",
            "COO",
            "Product",
            "Product",
            "Finance",
            "Finance",
            "HR",
            "HR",
        ],
        "target": [
            "CTO",
            "CFO",
            "COO",
            "Product",
            "Data",
            "Finance",
            "Legal",
            "HR",
            "Marketing",
            "Design",
            "Research",
            "Payroll",
            "Accounting",
            "Recruiting",
            "Training",
        ],
    }
)
fig = network(network_data, source="source", target="target")
