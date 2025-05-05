"""Dev app to try things out."""

from vizro.tables import dash_ag_grid

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
vm.Page.add_type("components", vm.Dropdown)


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


@capture("action")
def toggle_dropdown(is_disabled: bool):
    """Toggle dropdown's disabled state."""
    return not is_disabled


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


page_three = vm.Page(
    title="Explicit format example",
    components=[
        vm.Button(
            id="toggle_button",
            text="Toggle Dropdown",
            actions=[
                vm.Action(
                    function=toggle_dropdown(),
                    # We need to use explicit format here because we want to read the disabled state
                    inputs=["dropdown.disabled"],
                    outputs=["dropdown.disabled"],
                )
            ],
        ),
        vm.Dropdown(
            id="dropdown",
            title="Select a species:",
            options=df["species"].unique().tolist(),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_one, page_two, page_three])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
