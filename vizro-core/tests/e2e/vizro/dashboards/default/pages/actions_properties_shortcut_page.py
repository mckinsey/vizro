import time

import e2e.vizro.constants as cnst
import pandas as pd
from dash import ctx
from dash.exceptions import PreventUpdate

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

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


vm.Page.add_type("controls", vm.Button)

figures_title_header_footer_page = vm.Page(
    title=cnst.ACTION_PROPERTIES_SHORTCUT_TITLE_DESCRIPTION_HEADER_FOOTER_PAGE,
    id=cnst.ACTION_PROPERTIES_SHORTCUT_TITLE_DESCRIPTION_HEADER_FOOTER_PAGE,
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Graph(
            id=cnst.ACTION_SHORTCUT_GRAPH_ID,
            title=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            description=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            header=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            footer=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id=cnst.ACTION_SHORTCUT_AG_GRID_ID,
            title=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            description=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            header=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            footer=cnst.ACTION_PROPERTIES_SHORTCUT_DEFAULT_FIGURE_TEXT,
            figure=dash_ag_grid(df_3_rows),
        ),
    ],
    controls=[
        vm.Button(
            id=cnst.ACTION_SHORTCUT_TRIGGER_BUTTON_ID,
            actions=[
                vm.Action(
                    function=action_return_text(f"{cnst.ACTION_SHORTCUT_TRIGGER_BUTTON_ID}"),
                    outputs=[
                        # Graph
                        f"{cnst.ACTION_SHORTCUT_GRAPH_ID}.title",
                        f"{cnst.ACTION_SHORTCUT_GRAPH_ID}.description",
                        f"{cnst.ACTION_SHORTCUT_GRAPH_ID}.header",
                        f"{cnst.ACTION_SHORTCUT_GRAPH_ID}.footer",
                        # AgGrid
                        f"{cnst.ACTION_SHORTCUT_AG_GRID_ID}.title",
                        f"{cnst.ACTION_SHORTCUT_AG_GRID_ID}.description",
                        f"{cnst.ACTION_SHORTCUT_AG_GRID_ID}.header",
                        f"{cnst.ACTION_SHORTCUT_AG_GRID_ID}.footer",
                    ],
                )
            ],
        ),
    ],
)


@capture("action")
def action_select_ag_grid_rows(button_number_of_clicks):
    # Sleep to see what part of the output component is updating
    time.sleep(0.5)

    num_rows = button_number_of_clicks % 4
    selected_rows = df_3_rows.iloc[:num_rows].to_dict("records") if num_rows > 0 else []

    return selected_rows


ag_grid_underlying_id_shortcuts_page = vm.Page(
    title=cnst.AG_GRID_UNDERLYING_ID_SHORTCUTS_PAGE,
    id=cnst.AG_GRID_UNDERLYING_ID_SHORTCUTS_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.AG_GRID_SHORTCUTS_ID,
            title="Click button to update the figure",
            figure=dash_ag_grid(df_3_rows),
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: str(x))(f"{cnst.AG_GRID_SHORTCUTS_ID}.selectedRows"),
                    outputs=[cnst.CARD_SHORTCUTS_ID],
                )
            ],
        ),
        vm.Card(
            id=cnst.CARD_SHORTCUTS_ID,
            text="Click ag-grid cell to update me",
        ),
    ],
    controls=[
        vm.Button(
            id=cnst.BUTTON_AG_GRID_SHORTCUTS_ID,
            actions=[
                vm.Action(
                    function=action_select_ag_grid_rows(f"{cnst.BUTTON_AG_GRID_SHORTCUTS_ID}"),
                    outputs=[
                        f"{cnst.AG_GRID_SHORTCUTS_ID}.selectedRows",
                    ],
                )
            ],
        ),
    ],
)


actions_default_property_controls_page = vm.Page(
    title=cnst.ACTIONS_DEFAULT_PROPERTY_CONTROLS_PAGE,
    id=cnst.ACTIONS_DEFAULT_PROPERTY_CONTROLS_PAGE,
    components=[
        vm.Graph(
            id=cnst.SCATTER_DEFAULT_PROPERTY_CONTROLS_ID,
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.FILTER_DEFAULT_PROPERTY_CONTROLS,
            column="species",
            selector=vm.RadioItems(
                options=["sepal_length", "petal_length"],
                value="sepal_length",
                actions=vm.Action(
                    function=capture("action")(lambda x: x)(cnst.FILTER_DEFAULT_PROPERTY_CONTROLS),
                    outputs=cnst.PARAMETER_DEFAULT_PROPERTY_CONTROLS,
                ),
            ),
        ),
        vm.Parameter(
            id=cnst.PARAMETER_DEFAULT_PROPERTY_CONTROLS,
            targets=[f"{cnst.SCATTER_DEFAULT_PROPERTY_CONTROLS_ID}.x"],
            selector=vm.RadioItems(
                value="sepal_length",
                options=["sepal_length", "petal_length"],
            ),
        ),
    ],
)
