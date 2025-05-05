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


df = px.data.iris()


@capture("action")
def action_function(button_number_of_clicks):
    title = f"Button clicked {button_number_of_clicks} times."
    is_open = True if button_number_of_clicks % 2 == 0 else False
    return title, is_open


# ======= Page Smoke Test =======

page_smoke_test = vm.Page(
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

dashboard = vm.Dashboard(pages=[page_smoke_test])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
