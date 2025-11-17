from vizro import Vizro
import vizro.models as vm
from typing import Literal
from dash import html
import dash_bootstrap_components as dbc


class CustomDashboard(vm.Dashboard):
    type: Literal["custom_dashboard"] = "custom_dashboard"

    @staticmethod
    def custom_header():
        return [html.Div("Good morning, Li! ☕"), dbc.Badge("Tuesday", color="primary")]


page = vm.Page(title="Page Title", components=[vm.Card(text="""# Placeholder""")])
dashboard = CustomDashboard(pages=[page], title="Dashboard with custom header")
Vizro().build(dashboard).run()
