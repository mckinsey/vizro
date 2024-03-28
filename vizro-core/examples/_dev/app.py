"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data_class_action, filter_interaction
from vizro.tables import dash_ag_grid

df_gapminder = px.data.gapminder().query("year == 2007")


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Ag Grid - Filter interaction",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df_gapminder),
                    actions=[
                        vm.Action(
                            function=filter_interaction(
                                targets=[
                                    "scatter",
                                    # "scatter_from_page_2",
                                ]
                            )
                        )
                    ],
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
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(
                            function=export_data_class_action(
                                targets=[
                                    "scatter",
                                    # "scatter_from_page_2",
                                ]
                            )
                        )
                    ],
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
        vm.Page(
            title="Data Table - Filter interaction",
            components=[
                vm.Graph(
                    id="scatter_from_page_2",
                    figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", color="continent"),
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
