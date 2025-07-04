"""This is a test app to test the dashboard layout."""

from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html
import dash_bootstrap_components as dbc


class CustomDashboard(vm.Dashboard):
    """Dashboard with custom header."""

    type: Literal["custom_dashboard"] = "custom_dashboard"

    @staticmethod
    def custom_header():
        return [html.Div("Good morning, Li! ☕"), dbc.Badge("Tuesday", color="primary")]


page = vm.Page(title="Page Title", components=[vm.Card(text="""# Placerholder""")])


dashboard = CustomDashboard(pages=[page], title="Dashboard with custom header")

if __name__ == "__main__":
    Vizro().build(dashboard).run()
