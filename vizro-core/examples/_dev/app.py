"""Rough example used by developers."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table

df = px.data.gapminder()

table_and_container = vm.Page(
    title="Table and Container",
    components=[
        vm.Container(
            title="Container w/ Table",
            components=[
                vm.Table(
                    title="Table Title",
                    figure=dash_data_table(
                        id="dash_data_table_country",
                        data_frame=df,
                        page_size=30,
                    ),
                )
            ],
        ),
        vm.Container(
            title="Another Container",
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        title="Graph_2",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
        ),
    ],
    controls=[vm.Filter(column="continent")],
)


dashboard = vm.Dashboard(
    title="Dashboard Title",
    pages=[
        table_and_container,
    ],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
