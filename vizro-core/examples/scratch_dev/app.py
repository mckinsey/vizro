"""Scratch demo app"""

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro.models.types import capture
from vizro import Vizro
from vizro.tables import dash_ag_grid

selected_countries = [
    "Singapore",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
    "Vietnam",
    "Cambodia",
    "Myanmar",
]

gapminder = px.data.gapminder().query("country.isin(@selected_countries)")

gapminder_2007 = gapminder[gapminder["year"] == 2007]

page = vm.Page(
    title="Cross-filter a graph and table",
    components=[
        vm.Graph(
            id="bar_chart",
            figure=px.bar(
                gapminder_2007,
                x="lifeExp",
                y="country",
                labels={"lifeExp": "lifeExp in 2007"},
                category_orders={"country": sorted(gapminder_2007["country"]), "color": [False, True]},
            ),
            header="💡 Click on a bar to highlight the selected country and filter the table below",
            actions=[
                va.set_control(control="country_filter", value="y"),
            ],
        ),
        vm.AgGrid(id="gapminder_table", figure=dash_ag_grid(data_frame=gapminder)),
    ],
    controls=[
        vm.Filter(id="country_filter", column="country", targets=["gapminder_table"], visible=False),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
