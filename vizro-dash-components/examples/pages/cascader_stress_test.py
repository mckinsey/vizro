"""Cascader stress test: large synthetic tree for scroll, search, and panel performance."""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, html

dash.register_page(
    __name__,
    name="Cascader stress test",
    title="Cascader stress test",
)

STRESS_DEPTH = 5
STRESS_BRANCHES = (10, 2, 8, 5, 6)
STRESS_LEAVES_PER_TERMINAL = 2


def _count_leaves(node: dict | list) -> int:
    if isinstance(node, list):
        return len(node)
    return sum(_count_leaves(v) for v in node.values())


def _build_stress_tree() -> dict:
    def node(level: int, path: tuple[int, ...]) -> dict | list[str]:
        if level >= STRESS_DEPTH:
            p = ".".join(str(i) for i in path)
            return [f"item-{p}-{k}" for k in range(STRESS_LEAVES_PER_TERMINAL)]
        n_br = STRESS_BRANCHES[level]
        out: dict = {}
        for i in range(n_br):
            sub = (*path, i)
            key = f"lvl{level + 1}-{'.'.join(str(j) for j in sub)}"
            out[key] = node(level + 1, sub)
        return out

    return node(0, ())


STRESS_TREE = _build_stress_tree()
STRESS_LEAVES = _count_leaves(STRESS_TREE)

_COLUMN_STYLE = {
    "flex": "1 1 380px",
    "minWidth": "360px",
    "maxWidth": "520px",
}


def _output_column(title: str, component, output_id: str) -> html.Div:
    return html.Div(
        [
            dmc.Title(title, order=4, mb="xs"),
            component,
            dmc.Text(id=output_id, size="sm", c="dimmed", mt="sm"),
        ],
        style=_COLUMN_STYLE,
    )


layout = html.Div(
    [
        dmc.Text(
            f"Large synthetic tree: {STRESS_DEPTH} levels deep, branching "
            f"{STRESS_BRANCHES}, {STRESS_LEAVES_PER_TERMINAL} leaves per terminal → "
            f"{STRESS_LEAVES:,} leaf values. Use for scroll performance, search, and panel behavior.",
            c="dimmed",
            size="sm",
            mb="lg",
        ),
        dmc.Paper(
            [
                dmc.Title("Single-select", order=4, mb="sm"),
                _output_column(
                    "vdc.Cascader",
                    vdc.Cascader(
                        id="stress-cascade-single",
                        options=STRESS_TREE,
                        placeholder="Open panels…",
                        searchable=True,
                        clearable=True,
                        maxHeight=360,
                    ),
                    "stress-cascade-single-out",
                ),
                dmc.Divider(my="xl"),
                dmc.Title("Multi-select", order=4, mb="sm"),
                _output_column(
                    "vdc.Cascader",
                    vdc.Cascader(
                        id="stress-cascade-multi",
                        options=STRESS_TREE,
                        placeholder="Multi…",
                        multi=True,
                        searchable=True,
                        clearable=True,
                        maxHeight=360,
                        debounce=True,
                    ),
                    "stress-cascade-multi-out",
                ),
            ],
            p="lg",
            withBorder=True,
        ),
    ]
)


def _fmt_multi(v):
    return sorted(v) if v else v


@callback(Output("stress-cascade-single-out", "children"), Input("stress-cascade-single", "value"))
def _stress_cas_single(v):
    return f"Cascader: {v!r}"


@callback(Output("stress-cascade-multi-out", "children"), Input("stress-cascade-multi", "value"))
def _stress_cas_multi(v):
    return f"Cascader: {_fmt_multi(v)!r}"
