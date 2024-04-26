"""Example of cascading filters.
By selection 'continent' filter, the 'country' filter options (and value) is updated and the filtering action is
applied.
"""

from typing import Optional

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import update_figures
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df = px.data.gapminder()


@capture("action")
def set_country_filter_options_and_value(continent_filter_value: Optional[str] = None):
    countries = df[df["continent"] == continent_filter_value]["country"].unique()
    return countries, countries[0]


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Page_1",
            components=[vm.AgGrid(id="ag_grid", figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df))],
            controls=[
                vm.Filter(
                    column="continent",
                    selector=vm.Dropdown(
                        id="continent_filter",
                        multi=False,
                        value="Oceania",
                        actions=[
                            vm.Action(
                                function=set_country_filter_options_and_value(),
                                inputs=["continent_filter.value"],
                                outputs=["country_filter.options", "country_filter.value"],
                            ),
                            vm.Action(function=update_figures()),
                        ],
                    ),
                ),
                vm.Filter(column="country", selector=vm.Dropdown(id="country_filter")),
                vm.Filter(column="year"),
            ],
            actions=[
                vm.Action(
                    function=set_country_filter_options_and_value(),
                    inputs=["continent_filter.value"],
                    outputs=["country_filter.options", "country_filter.value"],
                ),
                vm.Action(function=update_figures()),
            ],
        ),
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
