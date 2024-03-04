"""Dev example of filter interaction with AgGrid and Graph components."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.tables import dash_ag_grid

df_gapminder = px.data.gapminder().query("year == 2007")

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Filter interaction",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df_gapminder),
                    actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
                ),
                vm.Graph(
                    id="scatter_relation_2007",
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

Vizro().build(dashboard).run()
