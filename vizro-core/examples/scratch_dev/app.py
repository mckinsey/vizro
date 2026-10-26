"""Scratch dev app: one page per new/canonical API introduced in this pre-stable release.

Each page exercises exactly one new API so it can be QA'd in isolation:

1. Slider(range=True)          - the merged range selector (replaces the deprecated RangeSlider).
2. set_controls               - the canonical action taking a list of control ids (replaces set_control).
3. Table(figure=dash_ag_grid) - the recommended AG Grid (replaces the deprecated AgGrid model).
4. Cascader(full_path=...)    - hierarchical selector with explicit full_path (default flips to True in 1.0.0).
5. Cascader (6 levels)        - deep tree for manually stress-testing the flyout chain (vizro-dash-components
                                 feat/cascader-redesign: viewport overflow, close/reopen positioning, etc).

Run with `hatch run example` from the vizro-core directory.
"""

import itertools

import pandas as pd
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

# ---------------------------------------------------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------------------------------------------------
iris = px.data.iris()
gapminder = px.data.gapminder()
gapminder_2007 = gapminder[gapminder["year"] == 2007]

# 6-level hierarchy, branching (5, 4, 3, 2, 2, 2) -> 480 leaf rows. Deep enough to open several
# simultaneous flyout columns (and push them toward/past the viewport edge) without being unwieldy
# to manually click through level by level. The deepest level's label encodes the full path (not
# just its own local index) so every leaf is globally unique, as leaf mode (full_path=False) requires.
_level_sizes = [5, 4, 3, 2, 2, 2]
_level_names = [f"level{i + 1}" for i in range(len(_level_sizes))]
deep_tree = pd.DataFrame(
    [
        {
            **{
                _level_names[i]: (
                    f"L{i + 1}-{idx[i]}" if i < len(idx) - 1 else f"L{i + 1}-" + ".".join(str(x) for x in idx)
                )
                for i in range(len(idx))
            },
            "value": sum(idx) + 1,
        }
        for idx in itertools.product(*(range(size) for size in _level_sizes))
    ]
)


# ---------------------------------------------------------------------------------------------------------------------
# 1. Slider(range=True) - replaces the deprecated RangeSlider.
# ---------------------------------------------------------------------------------------------------------------------
page_slider_range = vm.Page(
    title="Slider(range=True)",
    components=[
        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="sepal_length", selector=vm.Slider(range=True, title="Sepal length range")),
    ],
)


# ---------------------------------------------------------------------------------------------------------------------
# 2. set_controls - canonical action; `controls` is a list of ids. Click a point to set the continent filter.
# ---------------------------------------------------------------------------------------------------------------------
page_set_controls = vm.Page(
    title="set_controls",
    components=[
        vm.Graph(
            figure=px.scatter(gapminder_2007, x="gdpPercap", y="lifeExp", color="continent", custom_data="continent"),
            actions=va.set_controls(controls=["continent_filter"], value="continent"),
        ),
        vm.Graph(figure=px.box(gapminder_2007, x="continent", y="lifeExp", color="continent")),
    ],
    controls=[
        vm.Filter(id="continent_filter", column="continent", selector=vm.Dropdown()),
    ],
)


# ---------------------------------------------------------------------------------------------------------------------
# 3. Table(figure=dash_ag_grid(...)) - the recommended AG Grid, replacing the deprecated AgGrid model.
# ---------------------------------------------------------------------------------------------------------------------
page_ag_grid = vm.Page(
    title="Table (dash_ag_grid)",
    components=[
        vm.Table(title="Gapminder 2007", figure=dash_ag_grid(gapminder_2007)),
    ],
    controls=[
        vm.Filter(column="continent"),
    ],
)


# ---------------------------------------------------------------------------------------------------------------------
# 4. Cascader with explicit full_path - hierarchical selector (path mode becomes the default in 1.0.0).
# ---------------------------------------------------------------------------------------------------------------------
page_cascader = vm.Page(
    title="Cascader(full_path)",
    components=[
        vm.Graph(figure=px.scatter(gapminder_2007, x="gdpPercap", y="lifeExp", color="continent")),
    ],
    controls=[
        vm.Filter(
            column=["continent", "country"],
            selector=vm.Cascader(full_path=True, multi=True, title="Continent → country (path mode, multi)"),
        ),
        vm.Filter(
            column=["continent", "country"],
            selector=vm.Cascader(full_path=False, multi=True, title="Continent → country (leaf mode, multi)"),
        ),
        vm.Filter(
            column=["continent", "country"],
            selector=vm.Cascader(full_path=False, multi=False, title="Continent → country (leaf mode, single)"),
        ),
        vm.Filter(column=["continent", "country"], selector=vm.Cascader(title="Default (auto full_path)")),
    ],
)


# ---------------------------------------------------------------------------------------------------------------------
# 5. Cascader with a 6-level deep tree - manual stress test for the flyout-chain redesign.
# ---------------------------------------------------------------------------------------------------------------------
page_cascader_deep = vm.Page(
    title="Cascader (6 levels)",
    components=[
        vm.Graph(figure=px.bar(deep_tree, x="level1", y="value", color="level2")),
    ],
    controls=[
        vm.Filter(
            column=_level_names,
            selector=vm.Cascader(full_path=True, multi=True, title="6 levels (path mode, multi)"),
        ),
        vm.Filter(
            column=_level_names,
            selector=vm.Cascader(full_path=False, multi=False, title="6 levels (leaf mode, single)"),
        ),
    ],
)


dashboard = vm.Dashboard(
    title="New APIs scratch",
    pages=[
        page_slider_range,
        page_set_controls,
        page_ag_grid,
        page_cascader,
        page_cascader_deep,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
