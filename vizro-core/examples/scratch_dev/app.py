"""Scratch demo: Cascader vs Dropdown (same leaf set), each driving a custom Figure.

Tree size: set ``CASCADER_SHAPE`` to a tuple of positive ints — fan-out at each level, last entry is leaf list
length. Dict keys / list values use letters ``a``, ``b``, ``c``, … by depth (e.g. ``a_0``, ``b_0_1``,
``c_0_1_2``). Requires at least two entries (root must be a dict, not a list).
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
# Depth-first leaf order matches vdc Cascader normalization — Dropdowns use the same values, flattened
LEAF_VALUES = _iter_cascader_leaves_depth_first(CASCADER_OPTIONS)

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


page = vm.Page(
    title="Cascader demo",
    description=(
        f"**{' × '.join(str(n) for n in CASCADER_SHAPE)}** fan-out ({num_leaves} leaves). "
        "Same leaf values in the tree and in the dropdowns."
    ),
    components=[
        vm.Figure(
            id="echo_cascader_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_cascader_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_dropdown_single",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
        vm.Figure(
            id="echo_dropdown_multi",
            figure=selected_echo(data_frame=_DUMMY_DF),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["echo_cascader_single.selected"],
            selector=vm.Cascader(
                multi=False,
                title="Cascader multi=False",
                options=CASCADER_OPTIONS,
            ),
        ),
        vm.Parameter(
            targets=["echo_cascader_multi.selected"],
            selector=vm.Cascader(
                multi=True,
                title="Cascader multi=True",
                options=CASCADER_OPTIONS,
            ),
        ),
        vm.Parameter(
            targets=["echo_dropdown_single.selected"],
            selector=vm.Dropdown(
                multi=False,
                title="Dropdown multi=False",
                options=LEAF_VALUES,
            ),
        ),
        vm.Parameter(
            targets=["echo_dropdown_multi.selected"],
            selector=vm.Dropdown(
                multi=True,
                title="Dropdown multi=True",
                options=LEAF_VALUES,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
