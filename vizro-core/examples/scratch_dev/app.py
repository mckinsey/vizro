"""Scratch demo: hierarchical Cascader filter with dynamic data."""

import pandas as pd
from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.managers import data_manager
from vizro.models.types import capture

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


page_dynamic_df = vm.Page(
    title="Gapminder 2007 — dynamic hierarchical filter",
    components=[
        vm.Graph(
            id="scatter_dynamic",
            figure=px.scatter(
                "gapminder_dynamic",
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
                hover_name="country",
            ),
        ),
    ],
    controls=[
        vm.Filter(column=["continent", "region", "country"]),
        vm.Filter(column="country"),
        vm.Parameter(
            targets=["scatter_dynamic.data_frame.top_n_per_continent"],
            selector=vm.Slider(min=1, max=20, step=1, value=5, title="Top N per continent"),
        ),
    ],
)

page_static_df = vm.Page(
    title="Gapminder 2007 — static hierarchical filter",
    components=[
        vm.Graph(
            figure=px.scatter(
                load_gapminder(),
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
                hover_name="country",
            ),
        ),
    ],
    controls=[
        # Single-select with an explicit full-path default value, and shown in the URL to exercise the
        # path round-trip (?<id>=b64_...).
        vm.Filter(
            id="static_hier_filter",
            column=["continent", "region", "country"],
            selector=vm.Cascader(multi=False, value=["Americas", "North", "United States"]),
            show_in_url=True,
        ),
        vm.Filter(column="country"),
    ],
)

# Duplicate leaf labels across branches: "Portland" appears under both Oregon and Maine, and "Springfield"
# under both Oregon and Illinois. Each selection carries its full path, so they filter independently.
_cities = pd.DataFrame(
    {
        "state": ["Oregon", "Oregon", "Oregon", "Maine", "Maine", "Illinois", "Illinois"],
        "city": ["Portland", "Salem", "Springfield", "Portland", "Augusta", "Chicago", "Springfield"],
        "population": [652503, 175535, 62607, 66215, 18899, 2716000, 114230],
    }
)

page_duplicate_leaves = vm.Page(
    title="Duplicate leaf labels",
    components=[
        vm.Graph(figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        vm.Filter(column=["state", "city"], selector=vm.Cascader(multi=True)),
    ],
)

# --- Additional pages exercising value / options / multi / URL combinations for vm.Cascader ---

# Static tree reused by the Parameter page (Parameter selectors need explicit options, unlike Filter which
# derives them from the target data). Note "Portland" and "Springfield" are duplicated across states.
_city_tree: dict[str, list[str]] = {}
for _state, _city in zip(_cities["state"], _cities["city"]):
    _city_tree.setdefault(_state, [])
    if _city not in _city_tree[_state]:
        _city_tree[_state].append(_city)


@capture("graph")
def city_bar(data_frame, path=None):
    """Bar of city populations, optionally narrowed to a selected root-to-leaf path (state[/city])."""
    df = data_frame
    if path:
        for column, segment in zip(["state", "city"], path):
            df = df[df[column] == segment]
    label = " › ".join(map(str, path)) if path else "All"
    return px.bar(df, x="city", y="population", color="state", title=f"Selected path: {label}")


# Filter values supplied the LEGACY leaf-only way; each unique leaf is resolved to its full path.
page_legacy_values = vm.Page(
    title="Filter — legacy leaf values",
    components=[
        vm.Graph(id="legacy_single_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
        vm.Graph(id="legacy_multi_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        # Legacy single leaf: "Chicago" is unique, so it resolves to ["Illinois", "Chicago"].
        vm.Filter(
            column=["state", "city"],
            targets=["legacy_single_graph"],
            selector=vm.Cascader(multi=False, value="Chicago", title="Legacy single leaf ('Chicago')"),
        ),
        # Legacy multi leaves: each unique leaf resolves to its own path.
        vm.Filter(
            column=["state", "city"],
            targets=["legacy_multi_graph"],
            selector=vm.Cascader(multi=True, value=["Salem", "Augusta"], title="Legacy multi leaves"),
        ),
    ],
)

# No value supplied → the first leaf path is selected by default (mirrors Dropdown behavior).
page_default_values = vm.Page(
    title="Filter — default (no value)",
    components=[
        vm.Graph(id="default_single_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
        vm.Graph(id="default_multi_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        vm.Filter(
            column=["state", "city"],
            targets=["default_single_graph"],
            selector=vm.Cascader(multi=False, title="Single, no value"),
        ),
        vm.Filter(
            column=["state", "city"],
            targets=["default_multi_graph"],
            selector=vm.Cascader(multi=True, title="Multi, no value"),
        ),
    ],
)

# URL round-trip for both single and multi (nested paths are JSON+base64 encoded as ?<id>=b64_...).
page_url = vm.Page(
    title="URL persistence — single & multi",
    components=[
        vm.Graph(id="url_single_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
        vm.Graph(id="url_multi_graph", figure=px.bar(_cities, x="city", y="population", color="state")),
    ],
    controls=[
        vm.Filter(
            id="url_single_filter",
            column=["state", "city"],
            targets=["url_single_graph"],
            selector=vm.Cascader(multi=False, value=["Oregon", "Salem"], title="Single (in URL)"),
            show_in_url=True,
        ),
        vm.Filter(
            id="url_multi_filter",
            column=["state", "city"],
            targets=["url_multi_graph"],
            selector=vm.Cascader(
                multi=True, value=[["Illinois", "Chicago"], ["Maine", "Augusta"]], title="Multi (in URL)"
            ),
            show_in_url=True,
        ),
    ],
)

# Cascader inside a Parameter (options supplied explicitly), comparing legacy vs new value forms.
page_parameter = vm.Page(
    title="Parameter — Cascader (legacy vs new value)",
    components=[
        vm.Graph(id="param_new_graph", figure=city_bar(_cities)),
        vm.Graph(id="param_legacy_graph", figure=city_bar(_cities)),
    ],
    controls=[
        vm.Parameter(
            targets=["param_new_graph.path"],
            selector=vm.Cascader(options=_city_tree, multi=False, value=["Oregon", "Salem"], title="New path value"),
        ),
        vm.Parameter(
            targets=["param_legacy_graph.path"],
            selector=vm.Cascader(options=_city_tree, multi=False, value="Augusta", title="Legacy leaf value"),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_dynamic_df,
        page_static_df,
        page_duplicate_leaves,
        page_legacy_values,
        page_default_values,
        page_url,
        page_parameter,
    ]
)
if __name__ == "__main__":
    Vizro().build(dashboard).run()
