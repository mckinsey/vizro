"""Dev app to try things out."""

import pandas as pd

from dash import ctx
from dash.exceptions import PreventUpdate
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
    # Added to handle the bug when a page custom action is triggered if on-page-load is not defined
    if not button_number_of_clicks:
        raise PreventUpdate

    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    title = f"Button clicked {button_number_of_clicks} times."
    return [title] * (len(ctx.outputs_list) - 1)


@capture("action")
def action_return_figures(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    dff = px.data.iris().head(button_number_of_clicks % 4)

    return [
        px.scatter(dff, x="sepal_width", y="sepal_length", color="species"),
        dash_ag_grid(dff)(),
        dash_data_table(dff)(),
        kpi_card(dff, value_column="sepal_length")(),
    ]


@capture("action")
def action_select_ag_grid_rows(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    num_rows = button_number_of_clicks % 4
    selected_rows = df.iloc[:num_rows].to_dict("records") if num_rows > 0 else []

    return selected_rows


vm.Page.add_type("controls", vm.Button)


# ======= Page Table of Contents =======

page_table_of_contents = vm.Page(
    title="Table of Contents",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                # columnSize="sizeToFit",
                columnSize="autoSize",
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
                        ["Container", "", "", "title, description", ""],
                        ["Figure", "", "children", "figure", ""],
                        [
                            "AgGrid",
                            "",
                            "children",
                            "title, description, header, footer, figure",
                            "All 'outer-ID.property' are mapped to 'inner-ID.property'",
                        ],
                        ["Table", "", "children", "title, description, header, footer, figure", ""],
                        [
                            "Graph",
                            "",
                            "figure",
                            "title, description, header, footer",
                            "figure - works even without explicit mapping",
                        ],
                        ["Button", "", "", "text", ""],
                        ["Card", "", "children", "text", ""],
                        ["Text", "", "children", "text", ""],
                        ["Alert", "", "", "", ""],
                        ["TextArea", "value", "value", "title, description", ""],
                        ["UserInput", "value", "value", "title, description", ""],
                        ["Checklist", "value", "value", "title, description", ""],
                        ["DatePicker", "value", "value", "title, description", ""],
                        ["Dropdown", "value", "value", "title, description", ""],
                        ["RadioItems", "value", "value", "title, description", ""],
                        ["RangeSlider", "value", "value", "title, description", ""],
                        ["Slider", "value", "value", "title, description", ""],
                        ["Tabs", "", "", "title, description", ""],
                        ["Filter", "maybe in future", "children", "", ""],
                        ["Parameter", "maybe in future", "", "", ""],
                        ["Dashboard", "", "", "", ""],
                        ["Flex", "", "", "", ""],
                        ["Grid", "", "", "", ""],
                        ["Accordion", "", "", "", ""],
                        ["NavBar", "", "", "", ""],
                        ["NavLink", "", "", "", ""],
                        ["Navigation", "", "", "", ""],
                        ["Page", "", "", "title, description", ""],
                        ["Tooltip", "", "", "text, icon", ""],
                    ],
                ),
            )
        ),
    ],
)


# ======= Page Figures Title/Header/Footer =======

page_figures_title_header_footer = vm.Page(
    title="Graph/AgGrid/Table - title/description/header/footer",
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Graph(
            id="graph-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id="aggrid-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_ag_grid(df),
        ),
        vm.Table(
            id="table-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_data_table(df),
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-figures-title-header-footer-button-id",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-figures-title-header-footer-button-id.n_clicks"),
                    outputs=[
                        # Graph
                        "graph-id.title",
                        "graph-id.description",
                        "graph-id.header",
                        "graph-id.footer",
                        # AgGrid
                        "aggrid-id.title",
                        "aggrid-id.description",
                        "aggrid-id.header",
                        "aggrid-id.footer",
                        # Table
                        "table-id.title",
                        "table-id.description",
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
    title="Figures - figure output",
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


# ======= Page underlying ID shortcuts =======

page_ag_grid_underlying_id_shortcuts = vm.Page(
    title="AgGrid - underlying ID shortcuts",
    components=[
        vm.AgGrid(
            id="outer-aggrid-3-id",
            title="Click button to update the figure",
            figure=dash_ag_grid(df, dashGridOptions={"rowSelection": "multiple"}),
            actions=[
                # TODO-REVIEWER-CHECK: Before this PR, users had to assign the underlying-id to the dash_ag_grid
                #  and then to input it like "underlying_ag_grid_id.cellClicked"
                vm.Action(
                    function=capture("action")(lambda x: str(x))("outer-aggrid-3-id.cellClicked"), outputs=["card-3-id"]
                )
            ],
        ),
        vm.Card(
            id="card-3-id",
            text="## TODO-REVIEWER-CHECK: Click ag-grid cell to update me",
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-aggrid-3-id-button-id",
            actions=[
                vm.Action(
                    function=action_select_ag_grid_rows("trigger-aggrid-3-id-button-id.n_clicks"),
                    outputs=[
                        # TODO-REVIEWER-CHECK: Before this PR, users had to assign the underlying-id to the dash_ag_grid
                        #  and then to output it like "underlying_ag_grid_id.selectedRows"
                        "outer-aggrid-3-id.selectedRows",
                    ],
                )
            ],
        ),
    ],
)


# ======= Container title/description =======

page_container_title_description = vm.Page(
    title="Page/Container/Tabs - title/description",
    description="Click button to update me",
    components=[
        vm.Container(
            id="container-id",
            title="Click button to update me",
            description="Click button to update me",
            components=[vm.Text(text="Text component within the container. Blah blah...")],
        ),
        vm.Tabs(
            id="tabs-id",
            title="Click button to update me",
            description="Click button to update me",
            tabs=[
                vm.Container(
                    title="Container 1",
                    components=[vm.Text(text="Text component within the container. Blah blah...")],
                ),
                vm.Container(
                    title="Container 2",
                    components=[vm.Text(text="Text component within the container. Blah blah...")],
                ),
            ],
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-container-title-description-button-id",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-container-title-description-button-id.n_clicks"),
                    outputs=[
                        "Page/Container/Tabs - title/description.title",
                        "Page/Container/Tabs - title/description.description",
                        "container-id.title",
                        "container-id.description",
                        "tabs-id.title",
                        "tabs-id.description",
                    ],
                )
            ],
        ),
    ],
)


# ======= Card/Text Components =======

vm.Page.add_type("components", vm.Button)

page_card_text_components = vm.Page(
    title="Button/Card/Text - text",
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
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-card-text-button-id",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-card-text-button-id.n_clicks"),
                    outputs=[
                        "card-id.text",
                        "text-id.text",
                        "button-id.text",
                    ],
                    # TODO-REVIEWER-CHECK: This is also a valid output
                    # outputs=[
                    #   "card-id",
                    #   "text-id",
                    #   "button-id.text",
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
    title="TextArea/UserInput - title/description",
    components=[
        vm.TextArea(
            id="text-area-id",
            title="Click button to update me",
            description="Click button to update me",
        ),
        vm.UserInput(
            id="user-input-id",
            title="Click button to update me",
            description="Click button to update me",
        ),
    ],
    controls=[
        vm.Button(
            id="trigger-text-area-user-input-button-id",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-text-area-user-input-button-id.n_clicks"),
                    outputs=[
                        "text-area-id.title",
                        "text-area-id.description",
                        "user-input-id.title",
                        "user-input-id.description",
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
    title="Form Components - title/description",
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
    title="Dashboard for testing",
    pages=[
        page_table_of_contents,
        page_figures_title_header_footer,
        page_figures_figures,
        page_ag_grid_underlying_id_shortcuts,
        page_container_title_description,
        page_card_text_components,
        page_text_area_user_input_components,
        page_form_components,
    ],
    navigation=vm.Navigation(
        pages={
            "Table": ["Table of Contents"],
            "Figures": [
                "Graph/AgGrid/Table - title/description/header/footer",
                "Figures - figure output",
                "AgGrid - underlying ID shortcuts",
            ],
            "Components": [
                "Page/Container/Tabs - title/description",
                "Button/Card/Text - text",
                "TextArea/UserInput - title/description",
                "Form Components - title/description",
            ],
        }
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
