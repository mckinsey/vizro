"""Dev app to try things out."""

import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

from vizro.tables import dash_ag_grid


df = px.data.gapminder()

first_page = vm.Page(
    title="First Page",
    layout=vm.Layout(grid=[[0, 0], [1, 1], [1, 1], [1, 1]]),
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
    controls=[
        vm.Filter(column="continent", selector=vm.Checklist()),
        # vm.Filter(
        #     # column="country",
        #     column="continent",
        #     selector=vm.Dropdown(
        #         # options=[
        #         #     {"label": "EUROPE", "value": "Europe"},
        #         #     {"label": "AFRICA", "value": "Africa"},
        #         #     {"label": "ASIA", "value": "Asia"},
        #         #     {"label": "AMERICAS", "value": "Americas"},
        #         #     {"label": "OCEANIA", "value": "Oceania"},
        #         # ],
        #         # value=["Europe", "Africa", "Asia", "Americas", "Oceania"],
        #         # value="Europe",
        #         # multi=False,
        #     ),
        # ),
    ],
)

dashboard = vm.Dashboard(pages=[first_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
