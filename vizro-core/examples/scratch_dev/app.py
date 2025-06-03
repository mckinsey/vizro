from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

gapminder_2007 = px.data.gapminder().query("year == 2007")

page_1 = vm.Page(
    title="Collapsible containers bug",
    components=[
        vm.Container(
            title="Outer container - collapsible",
            collapsed=False,
            layout=vm.Flex(),
            components=[
                vm.Container(
                    collapsed=False,
                    title="First container - collapsible",
                    layout=vm.Flex(),
                    components=[vm.Card(text="First card"), vm.Card(text="Second card"), vm.Card(text="Third card")],
                ),
                vm.Container(
                    collapsed=False,
                    title="Second container - collapsible",
                    layout=vm.Flex(),
                    components=[vm.Card(text="First card"), vm.Card(text="Second card"), vm.Card(text="Third card")],
                ),
                vm.Container(
                    title="Third container - not collapsible",
                    layout=vm.Flex(),
                    components=[vm.Card(text="First card"), vm.Card(text="Second card"), vm.Card(text="Third card")],
                ),
            ],
        )
    ],
)

page_2 = vm.Page(
    title="Tab css issue",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab1",
                    components=[
                        vm.Graph(
                            title="Graph 1",
                            figure=px.bar(
                                gapminder_2007,
                                x="continent",
                                y="lifeExp",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab2",
                    components=[
                        vm.Graph(
                            title="Graph 2",
                            figure=px.scatter(
                                gapminder_2007,
                                x="gdpPercap",
                                y="lifeExp",
                                size="pop",
                                color="continent",
                            ),
                        ),
                    ],
                ),
                vm.Container(
                    title="Tab3",
                    layout=vm.Flex(),
                    components=[vm.Card(text="First card!"), vm.Card(text="Second card!"), vm.Card(text="Third card!")],
                ),
            ]
        )
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
