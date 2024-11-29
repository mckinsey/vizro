import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction, export_data

df_gapminder = px.data.gapminder().query("year == 2007")

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Filter interaction",
            components=[
                vm.Graph(
                    figure=px.box(
                        df_gapminder,
                        x="continent",
                        y="lifeExp",
                        color="continent",
                        custom_data=["continent"],
                    ),
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
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(function=export_data()),
                    ],
                ),
            ],
            controls=[
                vm.Filter(column="continent"),
                vm.Parameter(
                    id="parameter_x",
                    targets=["scatter_relation_2007.color"],
                    selector=vm.RadioItems(options=["continent", "pop"], id="x"),
                ),
            ],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
