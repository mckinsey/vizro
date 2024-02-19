"""Rough example used by developers."""

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

homepage = vm.Page(
    title="Homepage",
    description="Vizro demo app for studying gapminder data",
    layout=vm.Layout(grid=[[0, 1], [2, 3]], row_gap="16px", col_gap="24px"),
    components=[
        vm.Card(
            text="""
                ![](assets/images/icons/hypotheses.svg#icon-top)

                Analyzing population, GDP per capita and life expectancy on country and continent level.
                """,
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/hypotheses.svg#icon-top)

                Investigating the interconnection between population, GDP per capita and life expectancy.
                """,
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/collections.svg#icon-top)

                Summarizing the main findings for each continent.
                """,
        ),
        vm.Card(
            text="""
                ![](assets/images/icons/features.svg#icon-top)

                Discovering how the metrics differ for each country compared to the continent average
                and export data for further investigation.
                """,
        ),
    ],
)

cards = vm.Page(
    title="Cards",
    components=[
        vm.Card(
            text="""
                # This is an <h1> tag
                ## This is an <h2> tag
                ###### This is an <h6> tag

                >
                > Block quotes are used to highlight text.
                >

                * Item 1
                * Item 2

                *This text will be italic*

                _This will also be italic_

                **This text will be bold**

                _You **can** combine them_
            """
        )
    ],
)

dashboard = vm.Dashboard(pages=[homepage, cards])

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
