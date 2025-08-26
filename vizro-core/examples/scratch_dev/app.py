"""This is a test app to test the dashboard layout."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.gapminder()


page = vm.Page(
    id="page_1",
    title="Page 1",
    components=[
        vm.Container(
            title="Container 1",
            components=[vm.Graph(figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent"))],
            controls=[vm.Filter(column="continent", selector=vm.Checklist())],
            collapsed=False,
        ),
        vm.Container(
            title="Outer container",
            components=[
                vm.Container(
                    title="Inner container",
                    components=[vm.Graph(figure=px.bar(df, x="continent", y="lifeExp"))],
                    controls=[vm.Filter(column="continent", selector=vm.RadioItems())],
                    collapsed=True,
                )
            ],
            variant="filled",
        ),
    ],
)

page_2 = vm.Page(
    title="Controls in tabs",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Tab 1",
                    components=[
                        vm.Graph(figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent"))
                    ],
                    controls=[vm.Filter(column="continent", selector=vm.Checklist())],
                    collapsed=False,
                ),
                vm.Container(
                    title="Tab 2",
                    components=[vm.Graph(figure=px.bar(df, x="continent", y="lifeExp"))],
                    controls=[vm.Filter(column="continent", selector=vm.RadioItems())],
                    collapsed=True,
                ),
            ]
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page, page_2],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
