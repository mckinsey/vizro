"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid, dash_data_table

df_gapminder = px.data.gapminder().query("year == 2007")

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Ag Grid - Filter interaction",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df_gapminder),
                    actions=[vm.Action(function=filter_interaction(targets=["scatter"]))],
                ),
                vm.Graph(
                    id="scatter",
                    figure=px.scatter(
                        df_gapminder,
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
        vm.Page(
            title="Data Table - Filter interaction",
            components=[
                vm.Table(
                    figure=dash_data_table(data_frame=df_gapminder),
                    actions=[vm.Action(function=filter_interaction(targets=["scatter_2"]))],
                ),
                vm.Graph(
                    id="scatter_2",
                    figure=px.scatter(
                        df_gapminder,
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
