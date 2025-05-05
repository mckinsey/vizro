# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

"""Dev app to try things out."""

import time

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.figures import kpi_card

from typing import Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
import vizro.plotly.express as px
from dash import html
from vizro import Vizro

from vizro.models.types import capture


df = px.data.iris()


# 1. Create new custom component
class OffCanvas(vm.VizroBaseModel):
    type: Literal["offcanvas"] = "offcanvas"
    title: str
    content: str

    def build(self):
        return html.Div(
            [
                dbc.Offcanvas(
                    children=html.P(self.content),
                    id=self.id,
                    title=self.title,
                    is_open=False,
                ),
            ]
        )


vm.Page.add_type("components", OffCanvas)


@capture("action")
def action_function(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    is_open = True if button_number_of_clicks % 2 == 0 else False
    return title, is_open


@capture("action")
def open_offcanvas(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


page_one = vm.Page(
    title="Page Smoke Title",
    components=[
        vm.Button(
            id="trigger-button",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function(),
                    # This is how we had to define it before:
                    # inputs=["trigger-button-smoke-id.n_clicks"],
                    # outputs=["card-id.children"],
                    # Now we can just do this:
                    inputs=["trigger-button"],
                    outputs=["card-id", "tooltip-id"],
                )
            ],
        ),
        vm.Card(
            id="card-id",
            text="Click the button to update me",
        ),
        vm.AgGrid(figure=dash_ag_grid(df)),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                title="Species", description=vm.Tooltip(text="This is a tooltip", icon="info", id="tooltip-id")
            ),
        )
    ],
)

page_two = vm.Page(
    title="Custom Component",
    components=[
        vm.Button(
            text="Open Offcanvas",
            id="open_button",
            actions=[
                vm.Action(
                    function=open_offcanvas(),
                    inputs=["open_button", "offcanvas.is_open"],
                    outputs=["offcanvas.is_open"],
                )
            ],
        ),
        OffCanvas(
            id="offcanvas",
            content="OffCanvas content",
            title="Offcanvas Title",
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_one, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
