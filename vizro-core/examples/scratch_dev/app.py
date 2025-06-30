"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

from vizro.tables import dash_ag_grid


df = px.data.gapminder()

first_page = vm.Page(
    title="First Page",
    # layout=vm.Layout(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
    components=[
        vm.Container(
            title="Container with controls",
            layout=vm.Layout(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
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
                    figure=dash_ag_grid(data_frame=df, dashGridOptions={"pagination": True}),
                    title="Gapminder Data Insights",
                    header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
                    footer="""SOURCE: **Plotly gapminder data set, 2024**""",
                ),
            ],
            controls=[vm.Filter(column="continent", selector=vm.Checklist(title="Continent (checklist)"))],
        )
    ],
    controls=[
        # vm.Filter(column="continent"),
        vm.Filter(column="year", selector=vm.Dropdown()),
        vm.Filter(column="continent", selector=vm.Checklist()),
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

dashboard = vm.Dashboard(pages=[first_page])

if __name__ == "__main__":
    app = Vizro().build(dashboard)
    app.run()
