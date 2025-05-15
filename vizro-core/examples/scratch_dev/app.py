"""Dev app to try things out."""

import pandas as pd

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
def action_return_text(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    title = f"Button clicked {button_number_of_clicks} times."
    return [title] * (len(ctx.outputs_list) - 1)


@capture("action")
def action_return_figures(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    dff = px.data.iris().head(button_number_of_clicks % 3)

    return [
        px.scatter(dff, x="sepal_width", y="sepal_length", color="species"),
        dash_ag_grid(dff)(),
        dash_data_table(dff)(),
        kpi_card(dff, value_column="sepal_length")(),
    ]


vm.Page.add_type("controls", vm.Button)


# ======= Page Table of Contents =======

page_table_of_contents = vm.Page(
    title="Page Table of Contents Title",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                columnSize="sizeToFit",
                data_frame=pd.DataFrame(
                    columns=[
                        "Component",
                        "Default Input Property",
                        "Default Output Property",
                        "Additional output properties to support",
                        "Comment",
                    ],
                    data=[
                        ["Form", "", "", "", ""],
                        ["Container", "", "", "", ""],
                        ["Figure", "", "children", "figure", ""],
                        ["AgGrid", "", "children", "title, header, footer, figure", ""],
                        ["Table", "", "children", "title, header, footer, figure", ""],
                        [
                            "Graph",
                            "",
                            "figure",
                            "title, header, footer",
                            "figure - works even without explicit mapping",
                        ],
                        ["Button", "", "Not sure so don't do for now", "", ""],
                        ["Card", "", "children", "text", ""],
                        ["Text", "", "children", "text", ""],
                        ["Alert", "", "", "", ""],
                        [
                            "TextArea",
                            "value",
                            "value",
                            "title, * - description",
                            "* - description is not the model field",
                        ],
                        [
                            "UserInput",
                            "value",
                            "value",
                            "title, * - description",
                            "* - description is not the model field",
                        ],
                        ["Checklist", "value", "value", "title, description", ""],
                        ["DatePicker", "value", "value", "title, description", ""],
                        ["Dropdown", "value", "value", "title, description", ""],
                        ["RadioItems", "value", "value", "title, description", ""],
                        ["RangeSlider", "value", "value", "title, description", ""],
                        ["Slider", "value", "value", "title, description", ""],
                        ["Tabs", "", "", "", ""],
                        ["Filter", "maybe in future", "children", "", ""],
                        ["Parameter", "maybe in future", "", "", ""],
                        ["Dashboard", "", "", "", ""],
                        ["Flex", "", "", "", ""],
                        ["Grid", "", "", "", ""],
                        ["Accordion", "", "", "", ""],
                        ["NavBar", "", "", "", ""],
                        ["NavLink", "", "", "", ""],
                        ["Navigation", "", "", "", ""],
                        ["Page", "", "", "", ""],
                        ["Tooltip", "", "", "", ""],
                    ],
                ),
            )
        ),
    ],
)


# ======= Page Figures Title/Header/Footer =======


page_figures_title_header_footer = vm.Page(
    title="Graph/AgGrid/Table - title/header/footer",
    layout=vm.Grid(grid=[[0, 1, 2]]),
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
            figure=dash_ag_grid(df),
        ),
        vm.Table(
            id="table-id",
            title="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_data_table(df),
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-figures-title-header-footer-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-figures-title-header-footer-button-id.n_clicks"),
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
                    ],
                )
            ],
        ),
    ],
)


# ======= Page Figure figure =======

page_figures_figures = vm.Page(
    title="Figures - figures",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(
            id="graph-2-id",
            title="Click button to update the figure",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id="aggrid-2-id",
            title="Click button to update the figure",
            figure=dash_ag_grid(df),
        ),
        vm.Table(
            id="table-2-id",
            title="Click button to update the figure",
            figure=dash_data_table(df),
        ),
        vm.Figure(
            id="figure-2-id",
            figure=kpi_card(df, value_column="sepal_length"),
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-figures-figures-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_return_figures("trigger-figures-figures-button-id.n_clicks"),
                    outputs=[
                        "graph-2-id.figure",
                        "aggrid-2-id.figure",
                        "table-2-id.figure",
                        "figure-2-id.figure",
                    ],
                    # TODO-REVIEWER-CHECK: This is also a valid output
                    # outputs=[
                    #     "graph-2-id",
                    #     "aggrid-2-id",
                    #     "table-2-id",
                    #     "figure-2-id",
                    # ],
                )
            ],
        ),
    ],
)


# ======= Card/Text Components =======

page_card_text_components = vm.Page(
    title="Card/Text text",
    components=[
        vm.Card(
            id="card-id",
            text="Click button to update me",
        ),
        vm.Text(
            id="text-id",
            text="Click button to update me",
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-card-text-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-card-text-button-id.n_clicks"),
                    outputs=[
                        "card-id.text",
                        "text-id.text",
                    ],
                    # TODO-REVIEWER-CHECK: This is also a valid output
                    # outputs=[
                    #   "card-id",
                    #   "text-id",
                    # ],
                )
            ],
        ),
    ],
)


# # ======= TextArea/UserInput Components =======

vm.Page.add_type("components", vm.TextArea)
vm.Page.add_type("components", vm.UserInput)

page_text_area_user_input_components = vm.Page(
    title="TextArea/UserInput title",
    components=[
        vm.TextArea(
            id="text-area-id",
            title="Click button to update me",
        ),
        vm.UserInput(
            id="user-input-id",
            title="Click button to update me",
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-text-area-user-input-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-text-area-user-input-button-id.n_clicks"),
                    outputs=[
                        "text-area-id.title",
                        "user-input-id.title",
                    ],
                )
            ],
        ),
    ],
)


# ======= Form Components =======

vm.Page.add_type("components", vm.Dropdown)
vm.Page.add_type("components", vm.Checklist)
vm.Page.add_type("components", vm.RadioItems)
vm.Page.add_type("components", vm.Slider)
vm.Page.add_type("components", vm.RangeSlider)
vm.Page.add_type("components", vm.DatePicker)

page_form_components = vm.Page(
    title="Form Components Title/Description",
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
            id="trigger-form-components-title-description-button-id",
            text="Click me",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-form-components-title-description-button-id.n_clicks"),
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
                    ],
                )
            ],
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_table_of_contents,
        page_figures_title_header_footer,
        page_figures_figures,
        page_card_text_components,
        page_text_area_user_input_components,
        page_form_components,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
