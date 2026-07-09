"""Scratch demo: hierarchical Cascader filter with dynamic data."""

import pandas as pd
from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.managers import data_manager

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

dashboard = vm.Dashboard(pages=[page_dynamic_df, page_static_df, page_duplicate_leaves])
if __name__ == "__main__":
    Vizro().build(dashboard).run()
