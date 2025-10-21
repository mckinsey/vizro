from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid

gapminder = px.data.gapminder()
data_manager["df_dynamic"] = lambda: gapminder


page_1 = vm.Page(
    title="[BUG] #2271",
    layout=vm.Flex(),
    components=[
        vm.Text(text="Reset Dropdown(multi=True) control does not work when defined with non-list value"),
        vm.Text(text="https://github.com/McK-Internal/vizro-internal/issues/2271"),
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Dropdown [bug]",
                    controls=[
                        vm.Filter(column="year", selector=vm.Dropdown(value=2007)),
                        vm.Filter(column="continent", selector=vm.Dropdown(value="Europe")),
                    ],
                    components=[
                        vm.Graph(figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp", color="continent")),
                    ],
                ),
                vm.Container(
                    title="Checklist [works]",
                    controls=[
                        vm.Filter(column="year", selector=vm.Checklist(value=[2007])),
                    ],
                    components=[
                        vm.Graph(figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp", color="continent")),
                    ],
                ),
            ]
        ),
    ],
)


page_2 = vm.Page(
    title="[BUG] #1936",
    layout=vm.Flex(),
    components=[
        vm.Text(
            text="""
            Dynamic filters don't work with numeric columns which values can be translated to date objects by ISO 8601.
            For example, the 'year' column in the Gapminder dataset. It contains years as integers (1952, 1957...)
        """
        ),
        vm.Text(text="https://github.com/McK-Internal/vizro-internal/issues/1936"),
        vm.Container(
            controls=[
                vm.Filter(column="year", selector=vm.Slider()),
            ],
            components=[
                vm.Graph(figure=px.scatter("df_dynamic", x="gdpPercap", y="lifeExp", color="continent")),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_1, page_2])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
