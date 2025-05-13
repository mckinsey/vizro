# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

gapminder_2007 = px.data.gapminder().query("year == 2007")


def tabs(title: str, tab_title: str = ""):
    return vm.Tabs(
        title=tab_title,
        tabs=[
            vm.Container(
                title=f"{title} I",
                components=[
                    vm.Graph(
                        figure=px.bar(
                            gapminder_2007,
                            title="Graph 1",
                            x="continent",
                            y="lifeExp",
                            color="continent",
                        ),
                    ),
                    vm.Graph(
                        figure=px.box(
                            gapminder_2007,
                            title="Graph 2",
                            x="continent",
                            y="lifeExp",
                            color="continent",
                        ),
                    ),
                ],
            ),
            vm.Container(
                title=f"{title} II",
                components=[
                    vm.Graph(
                        figure=px.scatter(
                            gapminder_2007,
                            title="Graph 3",
                            x="gdpPercap",
                            y="lifeExp",
                            size="pop",
                            color="continent",
                        ),
                    ),
                ],
            ),
        ],
    )


page_zero = vm.Page(title="Tabs - Default", components=[tabs("Tab - Single")])
page_one = vm.Page(title="Tabs - Title", components=[tabs("Tab - Single", "Tab Title")])

page_two = vm.Page(
    title="Tabs inside Container",
    components=[vm.Container(title="Container Title", components=[tabs("Tab Container", "Tab Title")], variant="filled")],
)

page_three = vm.Page(
    title="Tabs inside Container - Collapsed",
    components=[
        vm.Container(
            title="Container Title Collapsed",
            components=[tabs("Tab Container Collapsed")],
            variant="filled",
            collapsed=True,
        )
    ],
)

dashboard = vm.Dashboard(pages=[page_zero,page_one, page_two, page_three])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
