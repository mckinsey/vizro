"""Cascader stress tests: two ~10k-leaf trees (deep uneven 6-level vs wide 2-level).

Each tree is rendered in both value modes side by side — leaf mode (`full_path=False`) and path
mode (`full_path=True`) — so their performance and emitted-value shapes can be compared directly.
The stress trees use globally-unique leaf values, so leaf mode is valid for them.
"""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
import vizro_dash_components as vdc
from dash import Input, Output, callback, html

dash.register_page(__name__, name="Cascader stress test")

MAX_WIDTH = 380
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

# Every (scenario, mode) pair; used to build the layout columns and register echo callbacks.
_SCENARIOS = [
    (
        "Deep tree",
        f"{DEEP_LEVELS} levels · branching {DEEP_BRANCHING} · "
        f"{DEEP_LEAVES_PER_TERMINAL} leaves per terminal → {DEEP_LEAF_COUNT:,} leaf values.",
        DEEP_TREE,
        "stress-deep",
    ),
    (
        "Wide tree",
        f"{WIDE_ROOT_COUNT} roots by {WIDE_LEAVES_PER_ROOT} leaves each → {WIDE_LEAF_COUNT:,} leaf values.",
        WIDE_TREE,
        "stress-wide",
    ),
]
_MODES = [("Leaf mode", "leaf", False), ("Path mode", "path", True)]


def _mode_column(mode_title: str, mode_key: str, full_path: bool, options: dict, prefix: str) -> dmc.Stack:
    single_id = f"{prefix}-{mode_key}-single"
    multi_id = f"{prefix}-{mode_key}-multi"
    return dmc.Stack(
        [
            dmc.Title(mode_title, order=4),
            dmc.Text(f"full_path={full_path}", c="dimmed", size="xs", mb="xs"),
            dmc.Text("Single-select", size="sm", fw=600),
            vdc.Cascader(
                id=single_id, options=options, full_path=full_path, placeholder="Single-select…", **_CASCADE_BASE
            ),
            dmc.Text(id=f"{single_id}-out", size="xs", c="dimmed"),
            dmc.Text("Multi-select", size="sm", fw=600, mt="sm"),
            vdc.Cascader(
                id=multi_id,
                options=options,
                full_path=full_path,
                multi=True,
                debounce=True,
                placeholder="Multi-select…",
                **_CASCADE_BASE,
            ),
            dmc.Text(id=f"{multi_id}-out", size="xs", c="dimmed"),
        ],
        style={"maxWidth": MAX_WIDTH},
        gap="xs",
    )


def _scenario(title: str, blurb: str, options: dict, prefix: str) -> html.Div:
    return html.Div(
        [
            dmc.Title(title, order=3, mb="xs"),
            dmc.Text(blurb, c="dimmed", size="sm", mb="md"),
            dmc.Group(
                [_mode_column(t, k, fp, options, prefix) for (t, k, fp) in _MODES],
                align="start",
                grow=True,
            ),
        ]
    )


layout = html.Div(
    [
        dmc.Title("Stress tests — leaf vs path", order=2, mb="sm"),
        dmc.Stack(
            [_scenario(title, blurb, options, prefix) for (title, blurb, options, prefix) in _SCENARIOS],
            gap="xl",
        ),
        html.Div(style={"height": "200px"}),
    ]
)


def _fmt(v):
    if isinstance(v, list):
        return sorted(v, key=repr)
    return v


def _register_echo(cid: str) -> None:
    @callback(Output(f"{cid}-out", "children"), Input(cid, "value"))
    def _echo(v):
        return f"Cascader: {_fmt(v)!r}"


for _prefix in ("stress-deep", "stress-wide"):
    for _mode_key in ("leaf", "path"):
        _register_echo(f"{_prefix}-{_mode_key}-single")
        _register_echo(f"{_prefix}-{_mode_key}-multi")
