"""Example of cascading filters.
    By selection 'continent' filter, the 'country' filter options (and value) is updated and the filtering action is
    applied.
"""
import pandas as pd
from typing import Optional, Dict, List, Any
import dash_ag_grid as dag
import vizro.models as vm
import vizro.plotly.express as px
from dash import ctx, dcc, Output, State, exceptions
from vizro import Vizro
from vizro.actions import export_data, filter_interaction, update_figures, filter_action
from vizro.managers._model_manager import ModelID
from vizro.tables import dash_ag_grid
from vizro.models.types import capture

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
                            vm.Action(function=update_figures())
                        ]
                    )
                ),
                vm.Filter(
                    column="country",
                    selector=vm.Dropdown(id="country_filter")
                ),
                vm.Filter(column="year"),
            ],
            actions=[
                vm.Action(
                    function=set_country_filter_options_and_value(),
                    inputs=["continent_filter.value"],
                    outputs=["country_filter.options", "country_filter.value"],
                ),
                vm.Action(function=update_figures())
            ]
        ),
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
