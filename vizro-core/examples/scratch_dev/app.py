"""Scratch demo: hierarchical Cascader filter with dynamic data."""

import pandas as pd
from vizro import Vizro
import vizro.actions as va
import vizro.plotly.express as px
import vizro.models as vm
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

_gapminder = px.data.gapminder().query("year == 2007").copy()
_regions = {
    "North": {
        "Canada",
        "United States",
        "Denmark",
        "Finland",
        "Norway",
        "Sweden",
        "Iceland",
        "Ireland",
        "United Kingdom",
        "Morocco",
        "Algeria",
        "Tunisia",
        "Libya",
        "Egypt",
        "Sudan",
        "Mongolia",
    },
    "South": {
        "Argentina",
        "Uruguay",
        "Paraguay",
        "Bolivia",
        "Chile",
        "Peru",
        "Italy",
        "Greece",
        "Spain",
        "Portugal",
        "Angola",
        "Zambia",
        "Malawi",
        "Mozambique",
        "Zimbabwe",
        "Botswana",
        "Namibia",
        "South Africa",
        "Lesotho",
        "Swaziland",
        "Madagascar",
        "Mauritius",
        "Reunion",
        "Comoros",
        "Bangladesh",
        "India",
        "Nepal",
        "Pakistan",
        "Sri Lanka",
        "Australia",
        "New Zealand",
    },
    "West": {
        "Mexico",
        "Costa Rica",
        "El Salvador",
        "Guatemala",
        "Honduras",
        "Nicaragua",
        "Panama",
        "Colombia",
        "Ecuador",
        "Venezuela",
        "France",
        "Belgium",
        "Netherlands",
        "Germany",
        "Switzerland",
        "Austria",
        "Senegal",
        "Gambia",
        "Guinea",
        "Guinea-Bissau",
        "Sierra Leone",
        "Liberia",
        "Cote d'Ivoire",
        "Ghana",
        "Togo",
        "Benin",
        "Nigeria",
        "Niger",
        "Burkina Faso",
        "Mali",
        "Mauritania",
        "Cameroon",
        "Central African Republic",
        "Chad",
        "Congo, Rep.",
        "Congo, Dem. Rep.",
        "Gabon",
        "Equatorial Guinea",
        "Sao Tome and Principe",
        "Afghanistan",
        "Iran",
        "Iraq",
        "Israel",
        "Jordan",
        "Lebanon",
        "Syria",
        "Turkey",
        "Saudi Arabia",
        "Kuwait",
        "Bahrain",
        "Oman",
        "Yemen, Rep.",
        "West Bank and Gaza",
    },
    "East": {
        "Brazil",
        "Cuba",
        "Dominican Republic",
        "Haiti",
        "Jamaica",
        "Puerto Rico",
        "Trinidad and Tobago",
        "Poland",
        "Czech Republic",
        "Slovak Republic",
        "Hungary",
        "Romania",
        "Bulgaria",
        "Serbia",
        "Montenegro",
        "Croatia",
        "Bosnia and Herzegovina",
        "Slovenia",
        "Albania",
        "Ethiopia",
        "Eritrea",
        "Djibouti",
        "Somalia",
        "Kenya",
        "Uganda",
        "Tanzania",
        "Rwanda",
        "Burundi",
        "China",
        "Hong Kong, China",
        "Japan",
        "Korea, Dem. Rep.",
        "Korea, Rep.",
        "Taiwan",
        "Cambodia",
        "Indonesia",
        "Malaysia",
        "Myanmar",
        "Philippines",
        "Singapore",
        "Thailand",
        "Vietnam",
    },
}
_gapminder["region"] = _gapminder["country"].map({c: r for r, cs in _regions.items() for c in cs})


def load_gapminder(top_n_per_continent: int = 5):
    """Return the top-N countries by population within each continent."""
    return (
        _gapminder.sort_values("pop", ascending=False)
        .groupby("continent", as_index=False, group_keys=False)
        .head(top_n_per_continent)
    )


data_manager["gapminder_dynamic"] = load_gapminder


# ===================================================================================================
# vm.Cascader has two modes, set by `full_path` (default False):
#   * LEAF MODE  (full_path=False): a selection is a bare leaf value; leaf labels must be unique across
#     the tree; a hierarchical Filter matches the LAST column; `set_control` is supported.
#   * PATH MODE  (full_path=True):  a selection is a full root-to-leaf path; duplicate leaf labels are
#     allowed and addressed unambiguously; a Filter matches EVERY column; `set_control` is disabled.
# Gapminder countries are globally unique → used for leaf-mode pages. The cities dataset has duplicate
# city names across states (two "Portland"s, two "Springfield"s) → used for path-mode pages.
# ===================================================================================================

# ---- LEAF MODE (default): gapminder, unique country leaves --------------------------------------

page_leaf_dynamic = vm.Page(
    title="Leaf mode - dynamic filter",
    components=[
        vm.Graph(
            id="scatter_leaf_single",
            figure=px.scatter(
                "gapminder_dynamic", x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country"
            ),
        ),
        vm.Graph(
            id="scatter_leaf_multi",
            figure=px.scatter(
                "gapminder_dynamic", x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country"
            ),
        ),
    ],
    controls=[
        # Leaf mode: options can be arbitrarily deep, rows match on the last column (`country`).
        # Single-select Cascader → its own graph.
        vm.Filter(
            id="leaf_dyn_single_filter",
            column=["continent", "region", "country"],
            targets=["scatter_leaf_single"],
            selector=vm.Cascader(multi=False, title="Country (single, leaf)"),
        ),
        # Multi-select Cascader → its own graph.
        vm.Filter(
            id="leaf_dyn_multi_filter",
            column=["continent", "region", "country"],
            targets=["scatter_leaf_multi"],
            selector=vm.Cascader(multi=True, title="Countries (multi, leaf)"),
        ),
        vm.Parameter(
            targets=[
                "scatter_leaf_single.data_frame.top_n_per_continent",
                "scatter_leaf_multi.data_frame.top_n_per_continent",
            ],
            selector=vm.Slider(min=1, max=20, step=1, value=5, title="Top N per continent"),
        ),
    ],
)

page_leaf_static = vm.Page(
    title="Leaf mode - static filter (URL)",
    components=[
        vm.Graph(
            id="leaf_static_single_graph",
            figure=px.scatter(
                load_gapminder(), x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country"
            ),
        ),
        vm.Graph(
            id="leaf_static_multi_graph",
            figure=px.scatter(
                load_gapminder(), x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country"
            ),
        ),
    ],
    controls=[
        # Single-select leaf value ("United States" is a unique country), shown in the URL as a scalar.
        vm.Filter(
            id="leaf_static_single_filter",
            column=["continent", "region", "country"],
            targets=["leaf_static_single_graph"],
            selector=vm.Cascader(multi=False, value="United States", title="Country (single, leaf)"),
            show_in_url=True,
        ),
        # Multi-select leaf values, shown in the URL as a list.
        vm.Filter(
            id="leaf_static_multi_filter",
            column=["continent", "region", "country"],
            targets=["leaf_static_multi_graph"],
            selector=vm.Cascader(multi=True, value=["United States", "China"], title="Countries (multi, leaf)"),
            show_in_url=True,
        ),
    ],
)

# ---- PATH MODE (full_path=True): cities, duplicate leaf labels ----------------------------------

# "Portland" appears under both Oregon and Maine, "Springfield" under both Oregon and Illinois.
_cities = pd.DataFrame(
    {
        "state": ["Oregon", "Oregon", "Oregon", "Maine", "Maine", "Illinois", "Illinois"],
        "city": ["Portland", "Salem", "Springfield", "Portland", "Augusta", "Chicago", "Springfield"],
        "population": [652503, 175535, 62607, 66215, 18899, 2716000, 114230],
    }
)

# Static tree reused by the path-mode Parameter (Parameter selectors need explicit options).
_city_tree: dict[str, list[str]] = {}
for _state, _city in zip(_cities["state"], _cities["city"]):
    _city_tree.setdefault(_state, [])
    if _city not in _city_tree[_state]:
        _city_tree[_state].append(_city)

page_path_duplicate = vm.Page(
    title="Path mode - duplicate leaves",
    components=[
        vm.Graph(id="path_dup_single_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
        vm.Graph(id="path_dup_multi_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        # Single-select path Cascader → its own graph: one full path, so a specific "Portland" is unambiguous.
        vm.Filter(
            id="path_dup_single_filter",
            column=["state", "city"],
            targets=["path_dup_single_graph"],
            selector=vm.Cascader(
                multi=False, full_path=True, value=["Oregon", "Portland"], title="City (single, path)"
            ),
        ),
        # Multi-select path Cascader → its own graph: the two "Portland"s filter independently.
        vm.Filter(
            id="path_dup_multi_filter",
            column=["state", "city"],
            targets=["path_dup_multi_graph"],
            selector=vm.Cascader(multi=True, full_path=True, title="Cities (multi, path)"),
        ),
    ],
)

page_path_url = vm.Page(
    title="Path mode - URL persistence",
    components=[
        vm.Graph(id="url_single_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
        vm.Graph(id="url_multi_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        vm.Filter(
            id="url_single_filter",
            column=["state", "city"],
            targets=["url_single_graph"],
            selector=vm.Cascader(multi=False, full_path=True, value=["Oregon", "Salem"], title="Single (in URL)"),
            show_in_url=True,
        ),
        vm.Filter(
            id="url_multi_filter",
            column=["state", "city"],
            targets=["url_multi_graph"],
            selector=vm.Cascader(
                multi=True,
                full_path=True,
                value=[["Illinois", "Chicago"], ["Maine", "Augusta"]],
                title="Multi (in URL)",
            ),
            show_in_url=True,
        ),
    ],
)


@capture("graph")
def city_bar(data_frame, path=None):
    """Bar of city populations, optionally narrowed to a selected root-to-leaf path (state[/city])."""
    df = data_frame
    if path:
        for column, segment in zip(["state", "city"], path):
            df = df[df[column] == segment]
    label = " › ".join(map(str, path)) if path else "All"
    return px.bar(df, x="city", y="population", color="state", title=f"Selected path: {label}")


@capture("graph")
def metric_bar(data_frame, y="lifeExp"):
    """Bar of a chosen (leaf) metric column — driven by a leaf-mode Cascader parameter."""
    return px.bar(data_frame.head(15), x="country", y=y, title=f"Metric: {y}")


# Cascader inside a Parameter: a leaf-mode metric picker and a path-mode city picker.
page_parameter = vm.Page(
    title="Parameter - leaf & path",
    components=[
        vm.Graph(id="param_leaf_graph", figure=metric_bar(load_gapminder())),
        vm.Graph(id="param_path_graph", figure=city_bar(_cities)),
    ],
    controls=[
        # Leaf mode: forwards the chosen leaf ("pop") to the target argument.
        vm.Parameter(
            targets=["param_leaf_graph.y"],
            selector=vm.Cascader(
                options={"Metrics": ["lifeExp", "pop", "gdpPercap"]}, multi=False, value="lifeExp", title="Metric"
            ),
        ),
        # Path mode: forwards the full path (e.g. ["Oregon", "Salem"]) to the target argument.
        vm.Parameter(
            targets=["param_path_graph.path"],
            selector=vm.Cascader(
                options=_city_tree, multi=False, full_path=True, value=["Oregon", "Salem"], title="City path"
            ),
        ),
    ],
)

# ---- set_control (leaf mode only; path mode raises at build) ------------------------------------
# A leaf-mode hierarchical Cascader behaves like a flat selector, so a trigger's single column value sets
# it directly. (A path-mode Cascader as a set_control target raises at build, because a trigger cannot
# reconstruct a full path — hence this demo uses leaf mode on the unique-country gapminder data.)

_gapminder_top = load_gapminder()

page_set_control_leaf = vm.Page(
    title="set_control - leaf mode",
    components=[
        # SOURCE: clicking a bar sends the clicked country (`x`), a leaf value.
        vm.Graph(
            id="sc_graph",
            figure=px.bar(_gapminder_top, x="country", y="pop", color="continent"),
            actions=[va.set_control(control="sc_filter", value="x")],
        ),
        # SOURCE: clicking a cell sends that row's `country`, a leaf value.
        vm.AgGrid(
            id="sc_grid_source",
            figure=dash_ag_grid(data_frame=_gapminder_top),
            actions=[va.set_control(control="sc_filter", value="country")],
        ),
        vm.Container(
            title="Buttons",
            layout=vm.Flex(direction="row"),
            components=[
                vm.Button(text="Show China", actions=[va.set_control(control="sc_filter", value="China")]),
                vm.Button(text="Show Brazil", actions=[va.set_control(control="sc_filter", value="Brazil")]),
                vm.Button(text="Reset filter", actions=[va.set_control(control="sc_filter", value=None)]),
            ],
        ),
        # TARGET: filtered by the cascader, so it reflects the current selection.
        vm.AgGrid(id="sc_grid_target", figure=dash_ag_grid(data_frame=_gapminder_top)),
    ],
    controls=[
        vm.Filter(
            id="sc_filter",
            column=["continent", "region", "country"],
            targets=["sc_grid_target"],
            selector=vm.Cascader(multi=True, value="China", title="Country (single, leaf mode)"),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_leaf_dynamic,
        page_leaf_static,
        page_path_duplicate,
        page_path_url,
        page_parameter,
        page_set_control_leaf,
    ]
)
if __name__ == "__main__":
    Vizro().build(dashboard).run()
