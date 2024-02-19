"""Rough example used by developers."""

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

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

graph = vm.Page(
    title="Graph",
    components=[
        vm.Graph(
            id="scatter_relation",
            figure=px.scatter(data_frame=px.data.gapminder(), x="gdpPercap", y="lifeExp", size="pop"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[cards, graph], navigation=vm.Navigation(nav_selector=vm.NavBar()))

if __name__ == "__main__":
    Vizro(external_stylesheets=[dbc.themes.BOOTSTRAP]).build(dashboard).run()
