"""Scratch dev app: one page per new/canonical API introduced in this pre-stable release.

Each page exercises exactly one new API so it can be QA'd in isolation:

1. Slider(range=True)          - the merged range selector (replaces the deprecated RangeSlider).
2. set_controls               - the canonical action taking a list of control ids (replaces set_control).
3. Table(figure=dash_ag_grid) - the recommended AG Grid (replaces the deprecated AgGrid model).
4. Cascader(full_path=...)    - hierarchical selector with explicit full_path (default flips to True in 1.0.0).

Run with `hatch run example` from the vizro-core directory.
"""

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
            selector=vm.Cascader(full_path=True, multi=True, title="Continent → country (path mode)"),
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
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
