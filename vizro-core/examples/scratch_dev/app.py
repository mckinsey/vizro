"""Scratch demo: Cascader vs Dropdown, hierarchical filters, set_control, and stress tests.

Page 1 tree size: set ``CASCADER_SHAPE`` to a tuple of positive ints (fan-out per level; last entry is leaf list
length). Dict keys / list values use letters ``a``, ``b``, ``c``, … by depth.

- **Page 1:** same comparison with page-level controls.
- **Page 2:** same four figure/parameter pairs, each parameter on a nested ``Container`` (outlined), 2x2 grid.
- **Page 3:** ``vm.Filter`` + hierarchical path columns in a DataFrame (same tree as page 1); echoes show the **filtered**
  ``data_frame`` (filters do not drive a ``.selected`` argument — use ``vm.Parameter`` for that, as on page 1).
- **Page 4:** ``set_control`` + ``Parameter`` with ``Cascader`` (single vs multi), driven by buttons.
- **Page 5:** stress cascaders built with ``_build_cascader_options`` (deep uneven shape and wide ``100 × 100``, ~10k+
  leaves each; aligned with ``vizro-dash-components/examples/pages/cascader_stress_test.py`` sizes).
"""

from __future__ import annotations

import math
import string
from typing import Any

import pandas as pd
import vizro.actions as va
import vizro.models as vm
from dash import dcc, html
from vizro import Vizro
from vizro.models._components.form.cascader import _iter_cascader_leaves_depth_first
from vizro.models.types import capture

# --- Helpers (recursive builders + @capture figures) ---


def _build_cascader_options(shape: tuple[int, ...], path_prefix: tuple[int, ...] = ()) -> dict[str, Any] | list[str]:
    def level_letter(depth: int) -> str:
        if 0 <= depth < len(string.ascii_lowercase):
            return string.ascii_lowercase[depth]
        return f"l{depth}"

    def label_at_depth(depth: int, path: tuple[int, ...]) -> str:
        return f"{level_letter(depth)}_" + "_".join(str(p) for p in path)

    if len(shape) == 1:
        if not path_prefix:
            msg = "CASCADER_SHAPE needs at least two ints (dict root + leaf list length)."
            raise ValueError(msg)
        n = shape[0]
        depth = len(path_prefix)
        return [label_at_depth(depth, (*path_prefix, i)) for i in range(n)]
    if not shape:
        msg = "CASCADER_SHAPE must not be empty."
        raise ValueError(msg)
    n_branch, *rest = shape
    depth = len(path_prefix)
    return {
        label_at_depth(depth, (*path_prefix, i)): _build_cascader_options(rest, (*path_prefix, i))
        for i in range(n_branch)
    }


def _leaf_count_from_branching(branching: tuple[int, ...], *, leaves_per_terminal: int = 1) -> int:
    """Leaf count for a uniform cascader tree: product of fan-outs at each level × terminal list length."""
    return math.prod(branching) * leaves_per_terminal


def _leaf_paths_from_cascader_options(options: dict[str, Any]) -> list[tuple[str, ...]]:
    """One tuple per leaf, root-to-leaf (same tree as ``CASCADER_OPTIONS`` / page 1)."""

    def walk(node: Any, prefix: tuple[str, ...]) -> list[tuple[str, ...]]:
        if isinstance(node, dict):
            rows: list[tuple[str, ...]] = []
            for k in sorted(node.keys(), key=lambda x: (type(x).__name__, str(x))):
                rows.extend(walk(node[k], (*prefix, str(k))))
            return rows
        if isinstance(node, list):
            return [(*prefix, str(leaf)) for leaf in node]
        return []

    return walk(options, ())


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


@capture("figure")
def hierarchical_filter_echo(data_frame: pd.DataFrame) -> html.Div:
    """Same line as ``selected_echo`` (`**Selected:** …`); value = distinct leaves in the last column after ``vm.Filter``."""
    if data_frame.empty:
        value: Any = None
    else:
        leaves = data_frame[data_frame.columns[-1]].dropna().unique()
        value = list(leaves) if len(leaves) > 0 else None
    return html.Div(dcc.Markdown(f"**Selected:** {_format_selected(value)}"))


# --- Demo data (constants for all pages) ---

# e.g. (10, 2, 10): ten ``a_*`` branches, two ``b_*_*`` each, ten ``c_*_*_*`` leaves per branch
CASCADER_SHAPE = (10, 2, 10)
CASCADER_OPTIONS = _build_cascader_options(CASCADER_SHAPE)
num_leaves = _leaf_count_from_branching(CASCADER_SHAPE)
LEAF_VALUES = _iter_cascader_leaves_depth_first(CASCADER_OPTIONS)

# Stress trees.
DEEP_SHAPE = (10, 2, 8, 8, 2)
DEEP_TREE = _build_cascader_options(DEEP_SHAPE)
DEEP_LEAF_COUNT = _leaf_count_from_branching(DEEP_SHAPE)

WIDE_SHAPE = (20, 300)
WIDE_TREE = _build_cascader_options(WIDE_SHAPE)
WIDE_LEAF_COUNT = _leaf_count_from_branching(WIDE_SHAPE)

# Placeholder DataFrame: vm.Figure + @capture("figure") always wire a data_frame argument
_DUMMY_DF = pd.DataFrame({"_": [0]})

_HIER_PATH_TUPLES = _leaf_paths_from_cascader_options(CASCADER_OPTIONS)
_HIER_PATH_DEPTH = len(_HIER_PATH_TUPLES[0])
HIER_FILTER_PATH_COLUMNS = [f"path_lvl{i}" for i in range(_HIER_PATH_DEPTH)]
HIER_FILTER_DF = pd.DataFrame(_HIER_PATH_TUPLES, columns=HIER_FILTER_PATH_COLUMNS)

SET_CONTROL_CASCADE_OPTIONS: dict[str, Any] = {
    "Asia": ["Tokyo", "Osaka"],
    "Europe": ["Paris", "Berlin"],
}

_COMPARE_DESCRIPTION = (
    f"**{' x '.join(str(n) for n in CASCADER_SHAPE)}** fan-out ({num_leaves} leaves). "
    "Same leaf values in the tree and in the dropdowns."
)
_COMPARE_CONTAINERS_DESCRIPTION = (
    _COMPARE_DESCRIPTION + " Parameters live on nested `Container` models (see `examples/dev/app.py`)."
)
_HIER_FILTER_PAGE_TEXT = (
    "**HIER_FILTER_DF** holds one row per leaf path in **CASCADER_OPTIONS** (same tree as page 1); columns "
    f"``{HIER_FILTER_PATH_COLUMNS}``. Two **hierarchical_filter_echo** figures (same **Selected:** line as page 1, "
    "value from filtered ``data_frame`` leaf column), each with **vm.Filter** + **Cascader** on the full path."
)
_SET_CONTROL_PAGE_TEXT = (
    "Buttons use **set_control** to set leaf values on two **Cascader** parameters (``multi=False`` vs ``multi=True``)."
)
_STRESS_PAGE_TEXT = (
    "Large option trees aligned with "
    "`vizro-dash-components/examples/pages/cascader_stress_test.py`. "
    f"**Deep:** shape **{' × '.join(str(n) for n in DEEP_SHAPE)}** "
    f"({len(DEEP_SHAPE) - 1} branch levels) → {DEEP_LEAF_COUNT:,} leaf values. "
    f"**Wide:** shape **{' × '.join(str(n) for n in WIDE_SHAPE)}** → {WIDE_LEAF_COUNT:,} leaf values."
)

# --- Pages (vm.Page + vm.Dashboard) ---


def _compare_page_figures_and_parameters(
    *,
    id_prefix: str,
    cascade_options: dict[str, Any] | None = None,
    flat_options: list[Any] | None = None,
) -> tuple[list[vm.Figure], list[vm.Parameter]]:
    """Shared by *Cascader vs dropdown* and *container controls* pages below."""
    co = CASCADER_OPTIONS if cascade_options is None else cascade_options
    flat_opts = LEAF_VALUES if flat_options is None else flat_options
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
                options=flat_opts,
            ),
        ),
        vm.Parameter(
            targets=[f"{id_prefix}dropdown_multi.selected"],
            selector=vm.Dropdown(
                multi=True,
                title="Dropdown multi=True",
                options=flat_opts,
            ),
        ),
    ]
    return figures, parameters


_compare_figures, _compare_parameters = _compare_page_figures_and_parameters(id_prefix="echo_")

page_compare = vm.Page(
    title="Cascader vs dropdown",
    layout=vm.Flex(),
    components=[
        vm.Text(text=_COMPARE_DESCRIPTION),
        *_compare_figures,
    ],
    controls=_compare_parameters,
)

_ct_figures, _ct_parameters = _compare_page_figures_and_parameters(id_prefix="echo_ct_")

page_compare_in_containers = vm.Page(
    title="Cascader vs dropdown (container controls)",
    layout=vm.Flex(),
    components=[
        vm.Text(text=_COMPARE_CONTAINERS_DESCRIPTION),
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
        ),
    ],
    controls=[],
)

page_hierarchical_filter = vm.Page(
    title="Hierarchical filter (static)",
    layout=vm.Flex(),
    components=[
        vm.Text(text=_HIER_FILTER_PAGE_TEXT),
        vm.Figure(
            id="hier_filter_cascader_single",
            figure=hierarchical_filter_echo(data_frame=HIER_FILTER_DF),
        ),
        vm.Figure(
            id="hier_filter_cascader_multi",
            figure=hierarchical_filter_echo(data_frame=HIER_FILTER_DF),
        ),
    ],
    controls=[
        vm.Filter(
            targets=["hier_filter_cascader_single"],
            column=HIER_FILTER_PATH_COLUMNS,
            selector=vm.Cascader(multi=False, title="Cascader multi=False"),
        ),
        vm.Filter(
            targets=["hier_filter_cascader_multi"],
            column=HIER_FILTER_PATH_COLUMNS,
            selector=vm.Cascader(multi=True, title="Cascader multi=True"),
        ),
    ],
)

page_set_control_cascader = vm.Page(
    title="set_control + Cascader",
    layout=vm.Flex(),
    components=[
        vm.Text(text=_SET_CONTROL_PAGE_TEXT),
        vm.Button(
            text="Set single cascader to Paris",
            actions=va.set_control(control="param_cascade_setctl_single", value="Paris"),
        ),
        vm.Button(
            text="Set multi cascader to Tokyo + Berlin",
            actions=va.set_control(control="param_cascade_setctl_multi", value=["Tokyo", "Berlin"]),
        ),
        vm.Figure(
            id="echo_setctl_cascader_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_setctl_cascader_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
    ],
    controls=[
        vm.Parameter(
            id="param_cascade_setctl_single",
            targets=["echo_setctl_cascader_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Cascader multi=False",
                options=SET_CONTROL_CASCADE_OPTIONS,
            ),
        ),
        vm.Parameter(
            id="param_cascade_setctl_multi",
            targets=["echo_setctl_cascader_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Cascader multi=True",
                options=SET_CONTROL_CASCADE_OPTIONS,
            ),
        ),
    ],
)

page_stress = vm.Page(
    title="Cascader stress test",
    layout=vm.Flex(),
    components=[
        vm.Text(text=_STRESS_PAGE_TEXT),
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
                extra={"placeholder": "Deep single-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_deep_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Deep tree — multi",
                options=DEEP_TREE,
                extra={"debounce": True, "placeholder": "Deep multi-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_wide_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Wide tree — single",
                options=WIDE_TREE,
                extra={"placeholder": "Wide single-select…"},
            ),
        ),
        vm.Parameter(
            targets=["echo_stress_wide_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Wide tree — multi",
                options=WIDE_TREE,
                extra={"debounce": True, "placeholder": "Wide multi-select…"},
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_compare,
        page_compare_in_containers,
        page_hierarchical_filter,
        page_set_control_cascader,
        # page_stress,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
