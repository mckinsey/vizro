from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
import pandas as pd
from vizro.tables import dash_ag_grid, dash_data_table

gapminder_2007 = px.data.gapminder().query("year == 2007")

page_1 = vm.Page(
    title="Grid AgGird",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.AgGrid(figure=dash_ag_grid(gapminder_2007)),
        vm.Graph(figure=px.scatter(gapminder_2007, x="continent", y="lifeExp")),
    ],
    controls=[vm.Filter(column="country")],
)

page_2 = vm.Page(
    title="Grid Table",
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Table(figure=dash_data_table(gapminder_2007)),
        vm.Graph(figure=px.scatter(gapminder_2007, x="continent", y="lifeExp")),
    ],
    controls=[vm.Filter(column="country")],
)

page_3 = vm.Page(
    title="Flex AgGird",
    layout=vm.Flex(direction="row"),
    components=[
        vm.AgGrid(figure=dash_ag_grid(gapminder_2007)),
        vm.Graph(figure=px.scatter(gapminder_2007, x="continent", y="lifeExp")),
    ],
    controls=[vm.Filter(column="country")],
)

page_4 = vm.Page(
    title="Flex Table",
    layout=vm.Flex(direction="row"),
    components=[
        vm.Table(figure=dash_data_table(gapminder_2007)),
        vm.Graph(figure=px.scatter(gapminder_2007, x="continent", y="lifeExp")),
    ],
    controls=[vm.Filter(column="country")],
)

page_5 = vm.Page(
    title="Page",
    layout=vm.Flex(),
    components=[
        vm.Card(text="""BLABLA"""),
        vm.Container(
            variant="outlined",
            title="Container with AgGrid",
            components=[vm.AgGrid(figure=dash_ag_grid(gapminder_2007))],
        ),
    ],
)

dashboard = vm.Dashboard(title="Test dashboard", pages=[page_1, page_2, page_3, page_4, page_5])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
