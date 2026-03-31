"""Cascader stress tests: two ~10k-leaf trees (deep uneven 6-level vs wide 2-level)."""

from __future__ import annotations

from dataclasses import dataclass

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, html

dash.register_page(
    __name__,
    name="Cascader stress test",
)

MAX_WIDTH = 400
PANEL_MAX_HEIGHT = 360

_CASCADE_BASE: dict = {
    "searchable": True,
    "clearable": True,
    "maxHeight": PANEL_MAX_HEIGHT,
}

# --- Deep tree: 6 levels, uneven branching (~10.8k leaves) ---

DEEP_LEVELS = 6
# One branch count per depth; intentionally uneven (not a uniform grid).
DEEP_BRANCHING = (10, 2, 8, 3, 8, 3)
DEEP_LEAVES_PER_TERMINAL = 2


def _count_leaves(node: dict | list) -> int:
    if isinstance(node, list):
        return len(node)
    return sum(_count_leaves(v) for v in node.values())


def _build_deep_tree() -> dict:
    def grow(level: int, path: tuple[int, ...]) -> dict | list[str]:
        if level >= DEEP_LEVELS:
            p = ".".join(str(i) for i in path)
            return [f"item-{p}-{k}" for k in range(DEEP_LEAVES_PER_TERMINAL)]
        n_br = DEEP_BRANCHING[level]
        out: dict = {}
        for i in range(n_br):
            sub = (*path, i)
            key = f"lvl{level + 1}-{'.'.join(str(j) for j in sub)}"
            out[key] = grow(level + 1, sub)
        return out

    return grow(0, ())


DEEP_TREE = _build_deep_tree()
DEEP_LEAF_COUNT = _count_leaves(DEEP_TREE)

# --- Wide tree: two levels (~10k leaves) ---

WIDE_ROOT_COUNT = 100
WIDE_LEAVES_PER_ROOT = 100
WIDE_TREE: dict[str, list[str]] = {
    f"cat-{i:03d}": [f"item-{i:03d}-{j:03d}" for j in range(WIDE_LEAVES_PER_ROOT)] for i in range(WIDE_ROOT_COUNT)
}
WIDE_LEAF_COUNT = WIDE_ROOT_COUNT * WIDE_LEAVES_PER_ROOT


@dataclass(frozen=True)
class _StressIds:
    single_id: str
    multi_id: str
    single_out: str
    multi_out: str


def _stress_scenario(title: str, blurb: str, options: dict, ids: _StressIds) -> list:
    base = {**_CASCADE_BASE, "options": options}
    return [
        dmc.Title(title, order=3, mb="xs"),
        dmc.Text(blurb, c="dimmed", size="sm", mb="lg"),
        dmc.Title("Single-select", order=4),
        html.Div(
            [
                vdc.Cascader(id=ids.single_id, placeholder="Single-select…", **base),
                dmc.Text(id=ids.single_out, size="sm", c="dimmed"),
            ],
            style={"maxWidth": MAX_WIDTH},
        ),
        dmc.Divider(),
        dmc.Title("Multi-select", order=4),
        html.Div(
            [
                vdc.Cascader(
                    id=ids.multi_id,
                    placeholder="Multi-select…",
                    multi=True,
                    debounce=True,
                    **base,
                ),
                dmc.Text(id=ids.multi_out, size="sm", c="dimmed"),
            ],
            style={"maxWidth": MAX_WIDTH},
        ),
    ]


layout = html.Div(
    [
        dmc.Title("Stress tests", order=2, mb="sm"),
        dmc.Stack(
            [
                *_stress_scenario(
                    "Deep tree",
                    f"{DEEP_LEVELS} levels · branching {DEEP_BRANCHING} · "
                    f"{DEEP_LEAVES_PER_TERMINAL} leaves per terminal → {DEEP_LEAF_COUNT:,} leaf values.",
                    DEEP_TREE,
                    _StressIds(
                        single_id="stress-single",
                        multi_id="stress-multi",
                        single_out="stress-single-out",
                        multi_out="stress-multi-out",
                    ),
                ),
                dmc.Divider(),
                *_stress_scenario(
                    "Wide tree",
                    f"{WIDE_ROOT_COUNT} roots by {WIDE_LEAVES_PER_ROOT} leaves each → {WIDE_LEAF_COUNT:,} leaf values.",
                    WIDE_TREE,
                    _StressIds(
                        single_id="stress-wide-single",
                        multi_id="stress-wide-multi",
                        single_out="stress-wide-single-out",
                        multi_out="stress-wide-multi-out",
                    ),
                ),
            ],
            gap="md",
        ),
    ]
)


def _fmt_multi(v):
    return sorted(v) if v else v


@callback(Output("stress-single-out", "children"), Input("stress-single", "value"))
def _stress_single(v):
    return f"Cascader: {v!r}"


@callback(Output("stress-multi-out", "children"), Input("stress-multi", "value"))
def _stress_multi(v):
    return f"Cascader: {_fmt_multi(v)!r}"


@callback(Output("stress-wide-single-out", "children"), Input("stress-wide-single", "value"))
def _stress_wide_single(v):
    return f"Cascader: {v!r}"


@callback(Output("stress-wide-multi-out", "children"), Input("stress-wide-multi", "value"))
def _stress_wide_multi(v):
    return f"Cascader: {_fmt_multi(v)!r}"
