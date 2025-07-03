"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro
from dash import html

from vizro.tables import dash_ag_grid
from vizro.managers import data_manager


df = px.data.gapminder()

first_page = vm.Page(
    title="First Page - Static data",
    # layout=vm.Grid(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
    components=[
        vm.Container(
            title="Container with controls",
            layout=vm.Grid(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
            variant="outlined",
            components=[
                vm.Card(
                    text="""
                        # First dashboard page
                        This pages shows the inclusion of markdown text in a page and how components
                        can be structured using Layout.
                    """,
                ),
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df),
                    title="Gapminder Data Insights",
                    header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
                    footer="""SOURCE: **Plotly gapminder data set, 2024**""",
                ),
            ],
            controls=[
                vm.Filter(
                    column="continent",
                    selector=vm.Checklist(
                        title="Continent (checklist)",
                    ),
                )
            ],
        )
    ],
    controls=[
        vm.Filter(column="continent", selector=vm.Dropdown()),
        vm.Filter(column="country", selector=vm.Dropdown(multi=False)),
        # vm.Filter(
        #     column="continent",
        #     selector=vm.Dropdown(
        #         options=[
        #             {"label": "EUROPE", "value": "Europe"},
        #             {"label": "AFRICA", "value": "Africa"},
        #             {"label": "ASIA", "value": "Asia"},
        #             # {"label": "AMERICAS", "value": "Americas"},
        #             # {"label": "OCEANIA", "value": "Oceania"},
        #         ],
        #         # value=["Europe", "Africa", "Asia", "Americas", "Oceania"],
        #         value="Asia",
        #         multi=False,
        #     ),
        # ),
    ],
)


def dynamic_data_load(number_of_rows: int = 1):
    return px.data.gapminder().head(number_of_rows)


data_manager["dynamic_df"] = dynamic_data_load


second_page = vm.Page(
    title="Second Page - Dynamic data",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="graph-1",
                    figure=px.scatter("dynamic_df", x="gdpPercap", y="lifeExp", color="continent"),
                )
            ],
            controls=[
                vm.Filter(id="page-2-filter-1", column="country"),
                vm.Filter(id="page-2-filter-2", column="continent", selector=vm.Checklist()),
            ]
        )
    ],
    controls=[
        vm.Parameter(
            id="page-2-parameter-1",
            targets=["graph-1.data_frame.number_of_rows"],
            selector=vm.Slider(
                id="number-of-rows-slider",
                title="Number of Rows",
                min=1,
                max=1000,
                step=100,
                value=1,
            )
        )
    ]
)

dashboard = vm.Dashboard(pages=[
    first_page,
    second_page,
])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
