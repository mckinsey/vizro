"""Scratch demo: Cascader vs Dropdown, edge cases, and stress tests.

Page 1 tree size: set ``CASCADER_SHAPE`` to a tuple of positive ints (fan-out per level; last entry is leaf list
length). Dict keys / list values use letters ``a``, ``b``, ``c``, … by depth.

- **Page 1:** same comparison with page-level controls.
- **Page 2:** same four figure/parameter pairs, each parameter on a nested ``Container`` (outlined), 2x2 grid.
- **Page 3:** duplicated leaf *values* on a two-level cascader (region → leaves); multi-select cascader vs dropdown
  only.
- **Page 4:** mirrors ``vizro-dash-components/examples/pages/cascader_stress_test.py`` (deep 6-level uneven tree and
  wide 100x100 tree, ~10k+ leaves each).
"""

from __future__ import annotations

import string
from functools import reduce
from operator import mul
from typing import Any

import pandas as pd
import vizro.models as vm
from dash import dcc, html
from vizro import Vizro
from vizro.models._components.form.cascader import _iter_cascader_leaves_depth_first
from vizro.models.types import capture


def _level_letter(depth: int) -> str:
    if 0 <= depth < len(string.ascii_lowercase):
        return string.ascii_lowercase[depth]
    return f"l{depth}"


def _label_at_depth(depth: int, path: tuple[int, ...]) -> str:
    return f"{_level_letter(depth)}_" + "_".join(str(p) for p in path)


def _build_cascader_options(shape: tuple[int, ...], path_prefix: tuple[int, ...] = ()) -> dict[str, Any] | list[str]:
    if len(shape) == 1:
        if not path_prefix:
            msg = "CASCADER_SHAPE needs at least two ints (dict root + leaf list length)."
            raise ValueError(msg)
        n = shape[0]
        depth = len(path_prefix)
        return [_label_at_depth(depth, (*path_prefix, i)) for i in range(n)]
    if not shape:
        msg = "CASCADER_SHAPE must not be empty."
        raise ValueError(msg)
    n_branch, *rest = shape
    depth = len(path_prefix)
    return {
        _label_at_depth(depth, (*path_prefix, i)): _build_cascader_options(rest, (*path_prefix, i))
        for i in range(n_branch)
    }


# e.g. (10, 2, 10): ten ``a_*`` branches, two ``b_*_*`` each, ten ``c_*_*_*`` leaves per branch
CASCADER_SHAPE = (10, 2, 10)
CASCADER_OPTIONS = _build_cascader_options(CASCADER_SHAPE)
num_leaves = reduce(mul, CASCADER_SHAPE, 1)
LEAF_VALUES = _iter_cascader_leaves_depth_first(CASCADER_OPTIONS)

# --- Stress trees (same as vizro-dash-components/examples/pages/cascader_stress_test.py) ---

DEEP_LEVELS = 6
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

WIDE_ROOT_COUNT = 100
WIDE_LEAVES_PER_ROOT = 100
WIDE_TREE: dict[str, list[str]] = {
    f"cat-{i:03d}": [f"item-{i:03d}-{j:03d}" for j in range(WIDE_LEAVES_PER_ROOT)] for i in range(WIDE_ROOT_COUNT)
}
WIDE_LEAF_COUNT = WIDE_ROOT_COUNT * WIDE_LEAVES_PER_ROOT

_STRESS_CASCADE_EXTRA_BASE: dict[str, Any] = {
    "searchable": True,
    "clearable": True,
    "maxHeight": 360,
}

# Placeholder DataFrame: vm.Figure + @capture("figure") always wire a data_frame argument
_DUMMY_DF = pd.DataFrame({"_": [0]})


def _format_selected(selected: Any) -> str:
    if selected is None:
        return "—"
    if isinstance(selected, list):
        return ", ".join(str(x) for x in selected) if selected else "—"
    return str(selected)


@capture("figure")
def selected_echo(
    data_frame: pd.DataFrame,
    selected: Any = None,
) -> html.Div:
    """Shows the parameter-driven `selected` value; `data_frame` is unused but required by `@capture('figure')`."""
    return html.Div(dcc.Markdown(f"**Selected:** {_format_selected(selected)}"))


def _compare_figures_and_parameters(
    *,
    id_prefix: str,
    cascade_options: dict[str, Any] | None = None,
    flat_options: list[Any] | None = None,
) -> tuple[list[vm.Figure], list[vm.Parameter]]:
    """Build four echo figures and matching cascader/dropdown parameters."""
    co = CASCADER_OPTIONS if cascade_options is None else cascade_options
    fo = LEAF_VALUES if flat_options is None else flat_options
    figures = [
        vm.Figure(
            id=f"{id_prefix}cascader_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id=f"{id_prefix}cascader_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id=f"{id_prefix}dropdown_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id=f"{id_prefix}dropdown_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
    ]
    parameters = [
        vm.Parameter(
            targets=[f"{id_prefix}cascader_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Cascader multi=False",
                options=co,
            ),
        ),
        vm.Parameter(
            targets=[f"{id_prefix}cascader_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Cascader multi=True",
                options=co,
            ),
        ),
        vm.Parameter(
            targets=[f"{id_prefix}dropdown_single.selected"],
            selector=vm.Dropdown(
                multi=False,
                title="Dropdown multi=False",
                options=fo,
            ),
        ),
        vm.Parameter(
            targets=[f"{id_prefix}dropdown_multi.selected"],
            selector=vm.Dropdown(
                multi=True,
                title="Dropdown multi=True",
                options=fo,
            ),
        ),
    ]
    return figures, parameters


_COMPARE_DESCRIPTION = (
    f"**{' x '.join(str(n) for n in CASCADER_SHAPE)}** fan-out ({num_leaves} leaves). "
    "Same leaf values in the tree and in the dropdowns."
)

_compare_figures, _compare_parameters = _compare_figures_and_parameters(id_prefix="echo_")

page_compare = vm.Page(
    title="Cascader vs dropdown",
    description=_COMPARE_DESCRIPTION,
    components=_compare_figures,
    controls=_compare_parameters,
)

_ct_figures, _ct_parameters = _compare_figures_and_parameters(id_prefix="echo_ct_")

page_compare_in_containers = vm.Page(
    title="Cascader vs dropdown (container controls)",
    description=_COMPARE_DESCRIPTION + " Parameters live on nested `Container` models (see `examples/dev/app.py`).",
    components=[
        vm.Container(
            layout=vm.Grid(grid=[[0, 1], [2, 3]]),
            components=[
                vm.Container(
                    components=[_ct_figures[i]],
                    controls=[_ct_parameters[i]],
                    variant="outlined",
                )
                for i in range(4)
            ],
        )
    ],
    controls=[],
)

# Two-level tree: region → leaf list. Same scalar appears under both regions.
DUP_LEAF_CASCADE: dict[str, Any] = {
    "East": ["shared_leaf", "east_only"],
    "West": ["shared_leaf", "west_only"],
}
DUP_LEAF_FLAT = _iter_cascader_leaves_depth_first(DUP_LEAF_CASCADE)

page_duplicate_leaves = vm.Page(
    title="Duplicated leaf values",
    description=(
        "Two-level cascader (region → leaves). The string **`shared_leaf`** appears under both **East** and **West**. "
        "The cascader keeps path context; the dropdown options list is the depth-first flatten "
        f"`{DUP_LEAF_FLAT}` (note the repeated value). Multi-select only."
    ),
    components=[
        vm.Figure(
            id="echo_dupleaf_cascader_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_dupleaf_dropdown_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["echo_dupleaf_cascader_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Cascader multi=True",
                options=DUP_LEAF_CASCADE,
            ),
        ),
        vm.Parameter(
            targets=["echo_dupleaf_dropdown_multi.selected"],
            selector=vm.Dropdown(
                multi=True,
                title="Dropdown multi=True",
                options=DUP_LEAF_FLAT,
            ),
        ),
    ],
)

page_stress = vm.Page(
    title="Cascader stress test",
    description=(
        "Large option trees aligned with "
        "`vizro-dash-components/examples/pages/cascader_stress_test.py`. "
        f"**Deep:** {DEEP_LEVELS} levels, branching {DEEP_BRANCHING}, "
        f"{DEEP_LEAVES_PER_TERMINAL} leaves per terminal → {DEEP_LEAF_COUNT:,} leaf values. "
        f"**Wide:** {WIDE_ROOT_COUNT} roots x {WIDE_LEAVES_PER_ROOT} leaves → {WIDE_LEAF_COUNT:,} leaf values."
    ),
    components=[
        vm.Figure(
            id="echo_stress_deep_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_stress_deep_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_stress_wide_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_stress_wide_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["echo_stress_deep_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Deep tree — single",
                options=DEEP_TREE,
                extra={**_STRESS_CASCADE_EXTRA_BASE, "placeholder": "Deep single-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_deep_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Deep tree — multi",
                options=DEEP_TREE,
                extra={**_STRESS_CASCADE_EXTRA_BASE, "debounce": True, "placeholder": "Deep multi-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_wide_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Wide tree — single",
                options=WIDE_TREE,
                extra={**_STRESS_CASCADE_EXTRA_BASE, "placeholder": "Wide single-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_wide_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Wide tree — multi",
                options=WIDE_TREE,
                extra={**_STRESS_CASCADE_EXTRA_BASE, "debounce": True, "placeholder": "Wide multi-select…"},
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page_compare, page_compare_in_containers, page_duplicate_leaves, page_stress],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
