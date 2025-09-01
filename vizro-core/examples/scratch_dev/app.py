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
from vizro.managers import data_manager

df = px.data.iris()

df["date_column"] = pd.date_range(start=pd.to_datetime("2024-01-01"), periods=len(df), freq="D")
df["number_column"] = range(len(df))
df["is_setosa"] = df["species"] == "setosa"

df_3_rows = df.head(3)
data_manager["dynamic_df"] = lambda number_of_rows=150: df.head(number_of_rows)


@capture("action")
def action_return_text(button_number_of_clicks):
    # Added to handle the bug when a page custom action is triggered if on-page-load is not defined
    if not button_number_of_clicks:
        raise PreventUpdate

    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    title = f"Button clicked {button_number_of_clicks} times."

    # -2 is set due to internal action outputs: "_action_finished" and "_action_progress_indicatior"
    return [title] * (len(ctx.outputs_list) - 2)


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
    selected_rows = df_3_rows.iloc[:num_rows].to_dict("records") if num_rows > 0 else []

    return selected_rows


vm.Page.add_type("controls", vm.Button)


# ======= Page Table of Contents =======

page_table_of_contents = vm.Page(
    title="Table of Contents",
    id="Table of Contents",
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(
                columnSize="autoSize",
                dashGridOptions={"pagination": False},
                data_frame=pd.DataFrame(
                    columns=[
                        "Component",
                        "Default Trigger Property",
                        "Default Input Property",
                        "Default Output Property",
                        "Additional output properties to support",
                        "Comment",
                    ],
                    data=[
                        ["Dashboard", "", "", "", "", ""],
                        ["Page", "{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", "", "", "title, description", ""],
                        [
                            "Graph",
                            "clickData",
                            "",
                            "figure",
                            "title, description, header, footer",
                            "figure - works even without explicit mapping",
                        ],
                        [
                            "AgGrid",
                            "{self._inner_component_id}.cellClicked",
                            "",
                            "children",
                            "title, description, header, footer, figure",
                            "All 'outer-ID.property' are mapped to 'inner-ID.property'",
                        ],
                        [
                            "Table",
                            "{self._inner_component_id}.active_cell",
                            "",
                            "children",
                            "title, description, header, footer, figure",
                            "",
                        ],
                        ["Figure", "", "", "children", "figure", ""],
                        ["Container", "", "", "", "title, description", ""],
                        ["Tabs", "", "", "", "title, description", ""],
                        ["Checklist", "value", "value", "value", "title, description", ""],
                        ["Dropdown", "value", "value", "value", "title, description", ""],
                        ["RadioItems", "value", "value", "value", "title, description", ""],
                        ["RangeSlider", "value", "value", "value", "title, description", ""],
                        ["Slider", "value", "value", "value", "title, description", ""],
                        ["DatePicker", "value", "value", "value", "title, description", ""],
                        ["Switch", "value", "value", "value", "title, description", ""],
                        [
                            "Filter",
                            "{self.selector}.value",
                            "{self.selector}.value",
                            "{self.selector}.value",
                            "selector, title, description",
                            "All 'filter-ID.property' are mapped to 'selector-ID.property'",
                        ],
                        [
                            "Parameter",
                            "{self.selector}.value",
                            "{self.selector}.value",
                            "{self.selector}.value",
                            "selector, title, description",
                            "All 'parameter-ID.property' are mapped to 'selector-ID.property'",
                        ],
                        ["Button", "n_clicks", "", "n_clicks", "text, description", ""],
                        ["Card", "", "", "children", "text", ""],
                        ["Text", "", "", "children", "text", ""],
                        ["TextArea", "", "value", "value", "title, description", ""],
                        ["UserInput", "", "value", "value", "title, description", ""],
                        ["Tooltip", "", "", "text", "text, icon", ""],
                        ["Form", "", "", "", "", ""],
                        ["Alert", "", "", "", "", ""],
                        ["Flex", "", "", "", "", ""],
                        ["Grid", "", "", "", "", ""],
                        ["Accordion", "", "", "", "", ""],
                        ["NavBar", "", "", "", "", ""],
                        ["NavLink", "", "", "", "", ""],
                        ["Navigation", "", "", "", "", ""],
                    ],
                ),
            )
        ),
    ],
)


# === FIGURES ===
# ======= Page Figures Title/Header/Footer =======

page_figures_title_header_footer = vm.Page(
    title="Graph/AgGrid/Table - title/description/header/footer",
    id="Graph/AgGrid/Table - title/description/header/footer",
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Graph(
            id="graph-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id="aggrid-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_ag_grid(df_3_rows),
        ),
        vm.Table(
            id="table-id",
            title="Click button to update me",
            description="Click button to update me",
            header="Click button to update me",
            footer="Click button to update me",
            figure=dash_data_table(df_3_rows),
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
    id="Figures - figure output",
    layout=vm.Grid(grid=[[0, 1], [2, 3]]),
    components=[
        vm.Graph(
            id="graph-2-id",
            title="Click button to update the figure",
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id="aggrid-2-id",
            title="Click button to update the figure",
            figure=dash_ag_grid(df_3_rows),
        ),
        vm.Table(
            id="table-2-id",
            title="Click button to update the figure",
            figure=dash_data_table(df_3_rows),
        ),
        vm.Figure(
            id="figure-2-id",
            figure=kpi_card(df_3_rows, value_column="sepal_length"),
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
    id="AgGrid - underlying ID shortcuts",
    components=[
        vm.AgGrid(
            id="outer-aggrid-3-id",
            title="Click button to update the figure",
            figure=dash_ag_grid(df_3_rows, dashGridOptions={"rowSelection": "multiple"}),
            actions=[
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
                        "outer-aggrid-3-id.selectedRows",
                    ],
                )
            ],
        ),
    ],
)


# === COMPONENTS ===
# ======= Container title/description =======

page_container_title_description = vm.Page(
    id="Page/Container/Tabs - title/description",
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
    id="Button/Card/Text - text",
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
    id="TextArea/UserInput - title/description",
    components=[
        vm.TextArea(
            id="text-area-id",
            title="Click button to update me",
            description="Click button to update me",
            placeholder="Blah blah...",
        ),
        vm.UserInput(
            id="user-input-id",
            title="Click button to update me",
            description="Click button to update me",
            placeholder="Blah blah...",
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
vm.Page.add_type("components", vm.Switch)

page_form_components = vm.Page(
    title="Form Components - title/description",
    id="Form Components - title/description",
    layout=vm.Grid(grid=[[0, 1, 2], [3, -1, 4], [5, -1, 6]]),
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
            step=10,
        ),
        vm.RangeSlider(
            id="range-slider-id",
            title="Click button to update me",
            description="Click button to update me",
            min=0,
            max=100,
            step=10,
        ),
        vm.DatePicker(
            id="date-picker-id",
            title="Click button to update me",
            description="Click button to update me",
            min="2023-01-01",
            max="2023-12-31",
        ),
        vm.Switch(
            id="switch-id",
            title="Click button to update me",
            description="Click button to update me",
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
                        # Switch
                        "switch-id.title",
                        "switch-id.description",
                    ],
                )
            ],
        ),
    ],
)


# ======= Tooltip text and icon =======

page_tooltip_text_icon = vm.Page(
    title="Tooltip - text and icon",
    id="Tooltip - text and icon",
    components=[
        vm.TextArea(
            id="text-area-tooltip-id",
            title="Click button to update the tooltip --> ",
            description=vm.Tooltip(
                id="tooltip-id",
                text="Click button to update me",
                icon="info",
            ),
        )
    ],
    controls=[
        vm.Button(
            id="trigger-tooltip-text-icon-button-id",
            actions=[
                vm.Action(
                    function=action_return_text("trigger-tooltip-text-icon-button-id.n_clicks"),
                    outputs=[
                        "tooltip-id.text",
                    ],
                    # outputs=[
                    #     "text-area-tooltip-id.description"
                    # ]
                ),
                vm.Action(
                    function=capture("action")(lambda x: "help" if x % 2 else "info")(
                        "trigger-tooltip-text-icon-button-id.n_clicks"
                    ),
                    outputs=[
                        "tooltip-id.icon",
                    ],
                ),
            ],
        ),
    ],
)


# === Controls ===
# ======= Page where Filter is output of the OPL and DFP =======

page_dynamic_filter_and_dfp = vm.Page(
    title="Filter is output of the OPL and DFP",
    id="Filter is output of the OPL and DFP",
    components=[
        vm.Graph(
            id="source_graph_2",
            figure=px.scatter(
                "dynamic_df", x="sepal_width", y="sepal_length", color="species", custom_data=["species"]
            ),
        ),
    ],
    controls=[
        vm.Filter(id="dynamic_filter", column="species"),
        vm.Parameter(
            id="df_parameter",
            targets=["source_graph_2.data_frame.number_of_rows"],
            selector=vm.Slider(
                id="data_frame_parameter_slider",
                min=10,
                max=150,
                value=150,
                step=10,
            ),
        ),
    ],
)

vm.Page.add_type("components", vm.Filter)
vm.Page.add_type("components", vm.Parameter)


# ======= Page Filter all selectors - default/title/description =======


@capture("action")
def update_control_values(
    n_clicks, dd_val=None, cl_val=None, ri_val=None, sl_val=None, rsl_val=None, dp_val=None, sw_val=None
):
    categorical_options = ["Option 1", "Option 2", "Option 3"]
    numerical_min = 10
    numerical_max = 100
    temporal_min = "2023-01-01"
    temporal_max = "2023-12-31"

    new_control_values = [
        categorical_options[: (n_clicks % 3 + 1)],
        categorical_options[: (n_clicks % 3 + 1)],
        categorical_options[: (n_clicks % 3 + 1)][-1],
        numerical_min * (n_clicks % 5),
        [numerical_min * (n_clicks % 5), numerical_max],
        [temporal_min.replace("01", f"0{n_clicks % 9 + 1}", 1), temporal_max],
        (n_clicks % 2 == 0),
    ]

    if dd_val:
        new_control_values += [
            f"Control inputs before this action: {dd_val} - {cl_val} - {ri_val} - {sl_val} - {rsl_val} - {dp_val} - {sw_val}"
        ]

    return new_control_values


page_filters_default_title_description = vm.Page(
    title="Filter all selectors - default/title/description",
    id="Filter all selectors - default/title/description",
    components=[
        vm.Container(
            title="Filter selectors",
            components=[vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species"))],
            controls=[
                vm.Filter(
                    id="filter-checklist-id",
                    column="species",
                    selector=vm.Checklist(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-dropdown-id",
                    column="species",
                    selector=vm.Dropdown(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-radio-items-id",
                    column="species",
                    selector=vm.RadioItems(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-slider-id",
                    column="sepal_length",
                    selector=vm.Slider(
                        title="Click button to update me",
                        description="Click button to update me",
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Filter(
                    id="filter-range-slider-id",
                    column="sepal_length",
                    selector=vm.RangeSlider(
                        title="Click button to update me",
                        description="Click button to update me",
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Filter(
                    id="filter-date-picker-id",
                    column="date_column",
                    selector=vm.DatePicker(
                        title="Click button to update me",
                        description="Click button to update me",
                        min="2023-01-01",
                        max="2023-12-31",
                    ),
                ),
                vm.Filter(
                    id="filter-switch-id",
                    column="is_setosa",
                    selector=vm.Switch(
                        title="Click button to update me",
                        description="Click button to update me",
                    ),
                ),
            ],
        )
    ],
    controls=[
        vm.Button(
            id="trigger-filter-all-selectors-default-title-description-button-id",
            actions=[
                vm.Action(
                    function=action_return_text(
                        "trigger-filter-all-selectors-default-title-description-button-id.n_clicks"
                    ),
                    outputs=[
                        # Checklist
                        "filter-checklist-id.title",
                        "filter-checklist-id.description",
                        # Dropdown
                        "filter-dropdown-id.title",
                        "filter-dropdown-id.description",
                        # RadioItems
                        "filter-radio-items-id.title",
                        "filter-radio-items-id.description",
                        # Slider
                        "filter-slider-id.title",
                        "filter-slider-id.description",
                        # RangeSlider
                        "filter-range-slider-id.title",
                        "filter-range-slider-id.description",
                        # DatePicker
                        "filter-date-picker-id.title",
                        "filter-date-picker-id.description",
                        # Switch
                        "filter-switch-id.title",
                        "filter-switch-id.description",
                    ],
                ),
                vm.Action(
                    function=update_control_values(
                        "trigger-filter-all-selectors-default-title-description-button-id.n_clicks"
                    ),
                    outputs=[
                        "filter-checklist-id",
                        "filter-dropdown-id",
                        "filter-radio-items-id",
                        "filter-slider-id",
                        "filter-range-slider-id",
                        "filter-date-picker-id",
                        "filter-switch-id",
                    ],
                ),
            ],
        ),
    ],
)


# ======= Page Filter all selectors - underlying value property =======

page_filters_underlying_value_property = vm.Page(
    title="Filter all selectors - underlying value property",
    id="Filter all selectors - underlying value property",
    components=[
        vm.Container(
            title="Filter selectors",
            components=[
                vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
                vm.Text(id="text-output", text="Click button to update me"),
            ],
            controls=[
                vm.Filter(
                    id="filter-checklist-2-id",
                    column="species",
                    selector=vm.Checklist(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-dropdown-2-id",
                    column="species",
                    selector=vm.Dropdown(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-radio-items-2-id",
                    column="species",
                    selector=vm.RadioItems(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Filter(
                    id="filter-slider-2-id",
                    column="sepal_length",
                    selector=vm.Slider(
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Filter(
                    id="filter-range-slider-2-id",
                    column="sepal_length",
                    selector=vm.RangeSlider(
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Filter(
                    id="filter-date-picker-2-id",
                    column="date_column",
                    selector=vm.DatePicker(
                        min="2023-01-01",
                        max="2023-12-31",
                    ),
                ),
                vm.Filter(
                    id="filter-switch-2-id",
                    column="is_setosa",
                    selector=vm.Switch(),
                ),
            ],
        )
    ],
    controls=[
        vm.Button(
            id="trigger-filter-all-selectors-underlying-value-property-button-id",
            actions=[
                vm.Action(
                    function=update_control_values(
                        "trigger-filter-all-selectors-underlying-value-property-button-id.n_clicks",
                        "filter-checklist-2-id.value",
                        "filter-dropdown-2-id.value",
                        "filter-radio-items-2-id.value",
                        "filter-slider-2-id.value",
                        "filter-range-slider-2-id.value",
                        "filter-date-picker-2-id.value",
                        "filter-switch-2-id.value",
                    ),
                    outputs=[
                        "filter-checklist-2-id.value",
                        "filter-dropdown-2-id.value",
                        "filter-radio-items-2-id.value",
                        "filter-slider-2-id.value",
                        "filter-range-slider-2-id.value",
                        "filter-date-picker-2-id.value",
                        "filter-switch-2-id.value",
                        "text-output",
                    ],
                ),
            ],
        ),
    ],
)


# ======= Page Parameter all selectors - default/title/description =======


@capture("graph")
def scatter_discards_parameters(data_frame, **kwargs):
    return px.scatter(data_frame, x="sepal_width", y="sepal_length", color="species")


page_parameters_default_title_description = vm.Page(
    title="Parameter all selectors - default/title/description",
    id="Parameter all selectors - default/title/description",
    components=[
        vm.Container(
            title="Parameter selectors",
            components=[vm.Graph(id="parameter-all-selectors-graph-id", figure=scatter_discards_parameters(df))],
            controls=[
                vm.Parameter(
                    id="parameter-checklist-id",
                    targets=["parameter-all-selectors-graph-id.checklist_value"],
                    selector=vm.Checklist(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-dropdown-id",
                    targets=["parameter-all-selectors-graph-id.dropdown_value"],
                    selector=vm.Dropdown(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-radio-items-id",
                    targets=["parameter-all-selectors-graph-id.radio_items_value"],
                    selector=vm.RadioItems(
                        title="Click button to update me",
                        description="Click button to update me",
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-slider-id",
                    targets=["parameter-all-selectors-graph-id.slider_value"],
                    selector=vm.Slider(
                        title="Click button to update me",
                        description="Click button to update me",
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Parameter(
                    id="parameter-range-slider-id",
                    targets=["parameter-all-selectors-graph-id.range_slider_value"],
                    selector=vm.RangeSlider(
                        title="Click button to update me",
                        description="Click button to update me",
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Parameter(
                    id="parameter-date-picker-id",
                    targets=["parameter-all-selectors-graph-id.date_picker_value"],
                    selector=vm.DatePicker(
                        title="Click button to update me",
                        description="Click button to update me",
                        min="2023-01-01",
                        max="2023-12-31",
                    ),
                ),
                vm.Parameter(
                    id="parameter-switch-id",
                    targets=["parameter-all-selectors-graph-id.switch_value"],
                    selector=vm.Switch(
                        title="Click button to update me",
                        description="Click button to update me",
                    ),
                ),
            ],
        )
    ],
    controls=[
        vm.Button(
            id="trigger-parameter-all-selectors-default-title-description-button-id",
            actions=[
                vm.Action(
                    function=action_return_text(
                        "trigger-parameter-all-selectors-default-title-description-button-id.n_clicks"
                    ),
                    outputs=[
                        # Checklist
                        "parameter-checklist-id.title",
                        "parameter-checklist-id.description",
                        # Dropdown
                        "parameter-dropdown-id.title",
                        "parameter-dropdown-id.description",
                        # RadioItems
                        "parameter-radio-items-id.title",
                        "parameter-radio-items-id.description",
                        # Slider
                        "parameter-slider-id.title",
                        "parameter-slider-id.description",
                        # RangeSlider
                        "parameter-range-slider-id.title",
                        "parameter-range-slider-id.description",
                        # DatePicker
                        "parameter-date-picker-id.title",
                        "parameter-date-picker-id.description",
                        # Switch
                        "parameter-switch-id.title",
                        "parameter-switch-id.description",
                    ],
                ),
                vm.Action(
                    function=update_control_values(
                        "trigger-parameter-all-selectors-default-title-description-button-id.n_clicks"
                    ),
                    outputs=[
                        "parameter-checklist-id",
                        "parameter-dropdown-id",
                        "parameter-radio-items-id",
                        "parameter-slider-id",
                        "parameter-range-slider-id",
                        "parameter-date-picker-id",
                        "parameter-switch-id",
                    ],
                ),
            ],
        ),
    ],
)


# ======= Page Parameter all selectors - underlying value property =======

page_parameters_underlying_value_property = vm.Page(
    title="Parameter all selectors - underlying value property",
    id="Parameter all selectors - underlying value property",
    components=[
        vm.Container(
            title="Parameter selectors",
            components=[
                vm.Graph(id="parameter-all-selectors-graph-2-id", figure=scatter_discards_parameters(df)),
                vm.Text(id="text-output-2", text="Click button to update me"),
            ],
            controls=[
                vm.Parameter(
                    id="parameter-checklist-2-id",
                    targets=["parameter-all-selectors-graph-2-id.checklist_value"],
                    selector=vm.Checklist(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-dropdown-2-id",
                    targets=["parameter-all-selectors-graph-2-id.dropdown_value"],
                    selector=vm.Dropdown(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-radio-items-2-id",
                    targets=["parameter-all-selectors-graph-2-id.radio_items_value"],
                    selector=vm.RadioItems(
                        options=["Option 1", "Option 2", "Option 3"],
                    ),
                ),
                vm.Parameter(
                    id="parameter-slider-2-id",
                    targets=["parameter-all-selectors-graph-2-id.slider_value"],
                    selector=vm.Slider(
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Parameter(
                    id="parameter-range-slider-2-id",
                    targets=["parameter-all-selectors-graph-2-id.range_slider_value"],
                    selector=vm.RangeSlider(
                        min=0,
                        max=100,
                        step=10,
                    ),
                ),
                vm.Parameter(
                    id="parameter-date-picker-2-id",
                    targets=["parameter-all-selectors-graph-2-id.date_picker_value"],
                    selector=vm.DatePicker(
                        min="2023-01-01",
                        max="2023-12-31",
                    ),
                ),
                vm.Parameter(
                    id="parameter-switch-2-id",
                    targets=["parameter-all-selectors-graph-2-id.switch_value"],
                    selector=vm.Switch(),
                ),
            ],
        )
    ],
    controls=[
        vm.Button(
            id="trigger-parameter-all-selectors-underlying-value-property-button-id",
            actions=[
                vm.Action(
                    function=update_control_values(
                        "trigger-parameter-all-selectors-underlying-value-property-button-id.n_clicks",
                        "parameter-checklist-2-id.value",
                        "parameter-dropdown-2-id.value",
                        "parameter-radio-items-2-id.value",
                        "parameter-slider-2-id.value",
                        "parameter-range-slider-2-id.value",
                        "parameter-date-picker-2-id.value",
                        "parameter-switch-2-id.value",
                    ),
                    outputs=[
                        "parameter-checklist-2-id.value",
                        "parameter-dropdown-2-id.value",
                        "parameter-radio-items-2-id.value",
                        "parameter-slider-2-id.value",
                        "parameter-range-slider-2-id.value",
                        "parameter-date-picker-2-id.value",
                        "parameter-switch-2-id.value",
                        "text-output-2",
                    ],
                ),
            ],
        ),
    ],
)


# ======= Filter interaction over Filter control (Graph clickData to Filter) =======

page_filter_interaction_over_control = vm.Page(
    title="Filter interaction over a control",
    id="Filter interaction over a control",
    components=[
        vm.Container(
            title="Source graph",
            components=[
                vm.Graph(
                    id="source_graph",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=vm.Action(
                        function=capture("action")(lambda x: x["points"][0]["customdata"][0])("source_graph.clickData"),
                        outputs="target_filter",
                    ),
                ),
            ],
        ),
        vm.Container(
            title="Target table",
            controls=[vm.Filter(id="target_filter", column="species")],
            components=[vm.AgGrid(figure=dash_ag_grid(df))],
        ),
    ],
)


# === _trigger ===
# ====== Page using _trigger: Filter interaction over a control ======

page_filter_interaction_over_control_using_trigger = vm.Page(
    title="Filter interaction over a control using _trigger",
    id="Filter interaction over a control using _trigger",
    components=[
        vm.Container(
            title="Source graph",
            components=[
                vm.Graph(
                    id="source_graph_trigger_page",
                    figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species", custom_data=["species"]),
                    actions=vm.Action(
                        # TODO-REVIEWER-CHECK: Before this PR, users had to assign the trigger-id to the actions
                        #  function like:"source_graph.clickData"
                        function=capture("action")(lambda _trigger: _trigger["points"][0]["customdata"][0])(),
                        outputs="_trigger_page_target_filter",
                    ),
                ),
            ],
        ),
        vm.Container(
            title="Target table",
            controls=[vm.Filter(id="_trigger_page_target_filter", column="species")],
            components=[vm.AgGrid(figure=dash_ag_grid(df))],
        ),
    ],
)


# ====== Page with chain of actions all using _trigger


@capture("action")
def propagate_trigger_to_output(_trigger):
    return f"_trigger: {_trigger}"


page_chain_of_actions_all_using_trigger = vm.Page(
    title="Chain of actions all using _trigger",
    id="Chain of actions all using _trigger",
    components=[
        vm.Card(id="card-1", text="Action 1 output"),
        vm.Card(id="card-2", text="Action 2 output"),
        vm.Card(id="card-3", text="Action 3 output"),
    ],
    controls=[
        vm.Button(
            actions=[
                vm.Action(function=propagate_trigger_to_output(), outputs="card-1"),
                vm.Action(function=propagate_trigger_to_output(), outputs="card-2"),
                vm.Action(function=propagate_trigger_to_output(), outputs="card-3"),
            ]
        )
    ],
)


# ====== Page with chain of actions all using _trigger and other inputs


@capture("action")
def propagate_trigger_and_other_inputs_to_output(other_input_1, _controls, other_input_2, _trigger):
    return (
        f"other_input_1: {other_input_1}, _controls: {_controls}, other_input_2: {other_input_2}, _trigger: {_trigger}"
    )


vm.Page.add_type("components", vm.RadioItems)
vm.Page.add_type("components", vm.Slider)

page_chain_of_actions_all_using_trigger_and_other_inputs = vm.Page(
    title="Chain of actions all using _trigger and other inputs",
    id="Chain of actions all using _trigger and other inputs",
    components=[
        vm.RadioItems(id="other_input_1", options=["A", "B", "C"], value="A"),
        vm.Slider(id="other_input_2", min=0, max=10, value=0),
        vm.Card(id="card-2-1", text="Action 1 output"),
        vm.Card(id="card-2-2", text="Action 2 output"),
        vm.Card(id="card-2-3", text="Action 3 output"),
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
    ],
    controls=[
        vm.Button(
            actions=[
                vm.Action(
                    function=propagate_trigger_and_other_inputs_to_output(
                        "other_input_1", other_input_2="other_input_2"
                    ),
                    outputs="card-2-1",
                ),
                vm.Action(
                    function=propagate_trigger_and_other_inputs_to_output(
                        "other_input_1", other_input_2="other_input_2"
                    ),
                    outputs="card-2-2",
                ),
                vm.Action(
                    function=propagate_trigger_and_other_inputs_to_output(
                        "other_input_1", other_input_2="other_input_2"
                    ),
                    outputs="card-2-3",
                ),
            ]
        ),
        vm.Filter(id="_trigger_page_filter", column="species"),
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
        page_tooltip_text_icon,
        page_dynamic_filter_and_dfp,
        page_filters_default_title_description,
        page_filters_underlying_value_property,
        page_parameters_default_title_description,
        page_parameters_underlying_value_property,
        page_filter_interaction_over_control,
        page_filter_interaction_over_control_using_trigger,
        page_chain_of_actions_all_using_trigger,
        page_chain_of_actions_all_using_trigger_and_other_inputs,
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
                "Tooltip - text and icon",
            ],
            "Controls": [
                "Filter is output of the OPL and DFP",
                "Filter all selectors - default/title/description",
                "Filter all selectors - underlying value property",
                "Parameter all selectors - default/title/description",
                "Parameter all selectors - underlying value property",
                "Filter interaction over a control",
            ],
            "**NEW**: _trigger": [
                "Filter interaction over a control using _trigger",
                "Chain of actions all using _trigger",
                "Chain of actions all using _trigger and other inputs",
            ],
        }
    ),
)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
