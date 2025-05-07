"""Dev app to try things out."""
from dash import ctx
import time

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.figures import kpi_card


df = px.data.iris().head(3)


@capture("action")
def action_function(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    title = f"Button clicked {button_number_of_clicks} times."
    return [title] * (len(ctx.outputs_list) - 1)


vm.Page.add_type("controls", vm.Button)


# ======= Page Smoke Test =======

page_smoke_test = vm.Page(
    title="Page Smoke Title",
    components=[
        vm.Graph(
            id="graph-smoke-id",
            title="Click button to update me",
            # title=" ",
            header="Click button to update me",
            footer="Click button to update me",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-button-smoke-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function("trigger-button-smoke-id.n_clicks"),
                    outputs=[
                        "graph-smoke-id.title",
                        "graph-smoke-id.header",
                        "graph-smoke-id.footer",
                    ],
                )
            ],
        )
    ]
)

# ======= Page Figures =======

page_figures = vm.Page(
    title="Page Figures Title",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(
            id="graph-id",
            title="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id="aggrid-id",
            title="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_ag_grid(df)
        ),
        vm.Table(
            id="table-id",
            title="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_data_table(df),
        ),
        vm.Figure(
            id="figure-id",
            figure=kpi_card(df, value_column="sepal_length"),
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-figures-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function("trigger-figures-button-id.n_clicks"),
                    outputs=[
                        # Graph
                        "graph-id.title",
                        "graph-id.header",
                        "graph-id.footer",
                        # AgGrid
                        "aggrid-id.title",
                        "aggrid-id.header",
                        "aggrid-id.footer",
                        # Table
                        "table-id.title",
                        "table-id.header",
                        "table-id.footer",
                        # Figure component does not have title, header and footer
                        # "figure-id.title",
                        # "figure-id.header",
                        # "figure-id.footer",
                    ]
                )
            ],
        ),
    ],
)

# ======= Other Components =======

page_other_components = vm.Page(
    title="Page Other Components Title",
    components=[
        vm.Tabs(
            id="tabs-id",
            tabs=[
                vm.Container(
                    id="container-id",
                    title="Click button to update me",
                    components=[
                        vm.Button(
                            id="button-id",
                            text="Click button to update me",
                        ),
                        vm.Card(
                            id="card-id",
                            text="Click button to update me",
                        ),
                        vm.Text(
                            id="text-id",
                            text="Click button to update me",
                        )
                    ],
                )
            ]
        )
    ],
    controls=[
        vm.Button(
            id="trigger-other-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function("trigger-other-button-id.n_clicks"),
                    outputs=[
                        # TODO: Tabs
                        # "tabs-id.tabs"
                        # TODO: Container
                        # "container-id.title",
                        # "container-id.collapsed",
                        # Button
                        "button-id.text",
                        "card-id.text",
                        "text-id.text",
                    ]
                )
            ],
        ),
    ]
)


# ======= Controls Components =======


# TODO: Make a page with Filter and Parameter as targets
#   - Add it to Dashboard.pages
# page_controls_components = vm.Page(...)


# ======= Form Components =======

vm.Page.add_type("components", vm.Dropdown)
vm.Page.add_type("components", vm.Checklist)
vm.Page.add_type("components", vm.RadioItems)
vm.Page.add_type("components", vm.Slider)
vm.Page.add_type("components", vm.RangeSlider)
vm.Page.add_type("components", vm.DatePicker)

page_form_components = vm.Page(
    title="Page Form Components Title",
    components=[
        vm.Checklist(
            id="checklist-id",
            title="Click button to update me",
            description="Click button to update me",
            options=["Option 1", "Option 2", "Option 3"],
        ),
        vm.Dropdown(
            id="dropdown-id",
            title="Click button to update me",
            description="Click button to update me",
            options=["Option 1", "Option 2", "Option 3"],
        ),
        vm.RadioItems(
            id="radio-id",
            title="Click button to update me",
            description="Click button to update me",
            options=["Option 1", "Option 2", "Option 3"],
        ),
        vm.Slider(
            id="slider-id",
            title="Click button to update me",
            description="Click button to update me",
            min=0,
            max=100,
            step=1,
        ),
        vm.RangeSlider(
            id="range-slider-id",
            title="Click button to update me",
            description="Click button to update me",
            min=0,
            max=100,
            step=1,
        ),
        vm.DatePicker(
            id="date-picker-id",
            title="Click button to update me",
            description="Click button to update me",
            min="2023-01-01",
            max="2023-12-31",
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-form-components-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_function("trigger-form-components-button-id.n_clicks"),
                    outputs=[
                        # Checklist
                        "checklist-id.title",
                        "checklist-id.description",
                        # Dropdown
                        "dropdown-id.title",
                        "dropdown-id.description",
                        # RadioItems
                        "radio-id.title",
                        "radio-id.description",
                        # Slider
                        "slider-id.title",
                        "slider-id.description",
                        # RangeSlider
                        "range-slider-id.title",
                        "range-slider-id.description",
                        # DatePicker
                        "date-picker-id.title",
                        "date-picker-id.description",
                    ]
                )
            ],
        ),
    ]
)

dashboard = vm.Dashboard(pages=[
    page_smoke_test,
    page_figures,
    page_other_components,
    page_form_components,
])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
