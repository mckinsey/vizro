import math
from collections import deque

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture
from vizro.themes._palettes import qualitative

HUB_RADIUS = 3  # distance of the first ring (level 1) from the central hub
LEVEL_SPACING = 3.5  # radial distance added per hierarchy level
MIN_NODE_SIZE = 15  # marker size for the least-connected node
NODE_SIZE_RANGE = 20  # extra marker size added for the most-connected node
DEFAULT_NODE_SIZE = 18  # marker size used when every node has the same degree


@capture("graph")
def network(data_frame: pd.DataFrame, source: str, target: str) -> go.Figure:
    """Radial, hierarchical network chart built from a table of source/target edge pairs."""
    G = nx.Graph()
    for s, t in zip(data_frame[source], data_frame[target]):
        G.add_edge(s, t)

    nodes = list(G.nodes())

    axis = {"showgrid": False, "zeroline": False, "showticklabels": False}
    layout = {"showlegend": False, "xaxis": axis, "yaxis": axis, "margin": {"l": 20, "r": 20, "t": 20, "b": 20}}

    if not nodes:
        return go.Figure(layout=layout)

    degree = dict(G.degree())
    hub = max(degree, key=lambda n: degree[n])

    # BFS from the hub to assign a level and parent to every reachable node.
    levels, parent = {hub: 0}, {hub: None}
    queue = deque([hub])
    while queue:
        current = queue.popleft()
        for n in G.neighbors(current):
            if n not in levels:
                levels[n] = levels[current] + 1
                parent[n] = current
                queue.append(n)

    pos = {hub: (0.0, 0.0)}
    level1 = [n for n in nodes if levels.get(n) == 1]

    if level1:
        sector = 2 * math.pi / len(level1)

        for i, n in enumerate(level1):
            angle = -math.pi / 2 + (i + 0.5) * sector
            pos[n] = (HUB_RADIUS * math.cos(angle), HUB_RADIUS * math.sin(angle))

        def place(pnode, pangle, psec, lvl):
            children = [n for n in nodes if parent.get(n) == pnode]
            if not children:
                return
            sec = psec * 0.35
            for i, c in enumerate(children):
                ang = pangle + (i - (len(children) - 1) / 2) * (sec / max(1, len(children) - 1))
                pos[c] = (lvl * LEVEL_SPACING * math.cos(ang), lvl * LEVEL_SPACING * math.sin(ang))
                place(c, ang, sec, lvl + 1)

        for i, n in enumerate(level1):
            place(n, -math.pi / 2 + (i + 0.5) * sector, sector, 2)

    # Place any nodes the BFS could not reach (disconnected components) on an outer fallback ring.
    missing = [n for n in nodes if n not in pos]
    if missing:
        outer_radius = LEVEL_SPACING * (max(levels.values(), default=0) + 1)
        ring_step = 2 * math.pi / len(missing)
        for i, n in enumerate(missing):
            angle = i * ring_step
            pos[n] = (outer_radius * math.cos(angle), outer_radius * math.sin(angle))

    node_x = [pos[n][0] for n in nodes]
    node_y = [pos[n][1] for n in nodes]

    min_d, max_d = min(degree.values()), max(degree.values())
    sizes = [
        MIN_NODE_SIZE + NODE_SIZE_RANGE * (degree[n] - min_d) / (max_d - min_d) if max_d > min_d else DEFAULT_NODE_SIZE
        for n in nodes
    ]
    node_colors = [qualitative[i % len(qualitative)] for i in range(len(nodes))]

    fig = go.Figure(layout=layout)
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
            marker={"size": sizes, "color": node_colors},
            text=nodes,
            textposition="top center",
            textfont={"size": 10},
            hoverinfo="text",
            hovertext=[f"{n}: {degree[n]}" for n in nodes],
        )
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
