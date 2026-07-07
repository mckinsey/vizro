# """Scratch demo: hierarchical Cascader filter with dynamic data."""
#
# from vizro import Vizro
# import vizro.plotly.express as px
# import vizro.models as vm
# from vizro.managers import data_manager
#
# _gapminder = px.data.gapminder().query("year == 2007").copy()
# _regions = {
#     "North": {
#         "Canada",
#         "United States",
#         "Denmark",
#         "Finland",
#         "Norway",
#         "Sweden",
#         "Iceland",
#         "Ireland",
#         "United Kingdom",
#         "Morocco",
#         "Algeria",
#         "Tunisia",
#         "Libya",
#         "Egypt",
#         "Sudan",
#         "Mongolia",
#     },
#     "South": {
#         "Argentina",
#         "Uruguay",
#         "Paraguay",
#         "Bolivia",
#         "Chile",
#         "Peru",
#         "Italy",
#         "Greece",
#         "Spain",
#         "Portugal",
#         "Angola",
#         "Zambia",
#         "Malawi",
#         "Mozambique",
#         "Zimbabwe",
#         "Botswana",
#         "Namibia",
#         "South Africa",
#         "Lesotho",
#         "Swaziland",
#         "Madagascar",
#         "Mauritius",
#         "Reunion",
#         "Comoros",
#         "Bangladesh",
#         "India",
#         "Nepal",
#         "Pakistan",
#         "Sri Lanka",
#         "Australia",
#         "New Zealand",
#     },
#     "West": {
#         "Mexico",
#         "Costa Rica",
#         "El Salvador",
#         "Guatemala",
#         "Honduras",
#         "Nicaragua",
#         "Panama",
#         "Colombia",
#         "Ecuador",
#         "Venezuela",
#         "France",
#         "Belgium",
#         "Netherlands",
#         "Germany",
#         "Switzerland",
#         "Austria",
#         "Senegal",
#         "Gambia",
#         "Guinea",
#         "Guinea-Bissau",
#         "Sierra Leone",
#         "Liberia",
#         "Cote d'Ivoire",
#         "Ghana",
#         "Togo",
#         "Benin",
#         "Nigeria",
#         "Niger",
#         "Burkina Faso",
#         "Mali",
#         "Mauritania",
#         "Cameroon",
#         "Central African Republic",
#         "Chad",
#         "Congo, Rep.",
#         "Congo, Dem. Rep.",
#         "Gabon",
#         "Equatorial Guinea",
#         "Sao Tome and Principe",
#         "Afghanistan",
#         "Iran",
#         "Iraq",
#         "Israel",
#         "Jordan",
#         "Lebanon",
#         "Syria",
#         "Turkey",
#         "Saudi Arabia",
#         "Kuwait",
#         "Bahrain",
#         "Oman",
#         "Yemen, Rep.",
#         "West Bank and Gaza",
#     },
#     "East": {
#         "Brazil",
#         "Cuba",
#         "Dominican Republic",
#         "Haiti",
#         "Jamaica",
#         "Puerto Rico",
#         "Trinidad and Tobago",
#         "Poland",
#         "Czech Republic",
#         "Slovak Republic",
#         "Hungary",
#         "Romania",
#         "Bulgaria",
#         "Serbia",
#         "Montenegro",
#         "Croatia",
#         "Bosnia and Herzegovina",
#         "Slovenia",
#         "Albania",
#         "Ethiopia",
#         "Eritrea",
#         "Djibouti",
#         "Somalia",
#         "Kenya",
#         "Uganda",
#         "Tanzania",
#         "Rwanda",
#         "Burundi",
#         "China",
#         "Hong Kong, China",
#         "Japan",
#         "Korea, Dem. Rep.",
#         "Korea, Rep.",
#         "Taiwan",
#         "Cambodia",
#         "Indonesia",
#         "Malaysia",
#         "Myanmar",
#         "Philippines",
#         "Singapore",
#         "Thailand",
#         "Vietnam",
#     },
# }
# _gapminder["region"] = _gapminder["country"].map({c: r for r, cs in _regions.items() for c in cs})
#
#
# def load_gapminder(top_n_per_continent: int = 5):
#     """Return the top-N countries by population within each continent."""
#     return (
#         _gapminder.sort_values("pop", ascending=False)
#         .groupby("continent", as_index=False, group_keys=False)
#         .head(top_n_per_continent)
#     )
#
#
# data_manager["gapminder_dynamic"] = load_gapminder
#
#
# page = vm.Page(
#     title="Gapminder 2007 — dynamic hierarchical filter",
#     components=[
#         vm.Graph(
#             id="scatter",
#             figure=px.scatter(
#                 "gapminder_dynamic",
#                 x="gdpPercap",
#                 y="lifeExp",
#                 size="pop",
#                 color="continent",
#                 hover_name="country",
#             ),
#         ),
#     ],
#     controls=[
#         vm.Filter(column=["continent", "region", "country"]),
#         vm.Filter(column="country"),
#         vm.Parameter(
#             targets=["scatter.data_frame.top_n_per_continent"],
#             selector=vm.Slider(min=1, max=20, step=1, value=5, title="Top N per continent"),
#         ),
#     ],
# )
#
# dashboard = vm.Dashboard(pages=[page])
# if __name__ == "__main__":
#     Vizro().build(dashboard).run()

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = pd.DataFrame(
    {
        "region": ["Europe", "Europe", "Asia"],
        "as_of": pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31"]),  # datetime column
        "sales": [10, 20, 30],
    }
)

page = vm.Page(
    title="Sales",
    components=[vm.Graph(figure=px.bar(df, x="region", y="sales"))],
    controls=[vm.Filter(column=["region", "as_of"])],  # hierarchical filter, date-typed leaf
)

if __name__ == "__main__":
    Vizro().build(vm.Dashboard(pages=[page])).run()
