"""This is a test app to test the dashboard layout."""

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html
import dash_bootstrap_components as dbc

df = px.data.iris()


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard."""

    type: Literal["custom_dashboard"] = "custom_dashboard"

    def custom_header(self):
        # single_component = html.Div("Welcome Li!")
        multiple_components = [html.Div("Welcome Li!"), dbc.Badge("Badge", color="primary")]
        return multiple_components


page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)


dashboard = CustomDashboard(pages=[page], title="Dashboard Title")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
