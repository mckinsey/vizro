import e2e.vizro.constants as cnst
import pandas as pd

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
    title = f"Button clicked {button_number_of_clicks} times."

    # There are 8 identical outputs (4 for graph and 4 for ag_grid)
    return [title] * 8


vm.Page.add_type("controls", vm.Button)

action_model_field_shortcut_page = vm.Page(
    title=cnst.ACTION_MODEL_FIELD_SHORTCUT_PAGE,
    id=cnst.ACTION_MODEL_FIELD_SHORTCUT_PAGE,
    layout=vm.Grid(grid=[[0, 1]]),
    components=[
        vm.Graph(
            id=cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID,
            title=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            description=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            header=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            footer=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
        vm.AgGrid(
            id=cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID,
            title=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            description=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            header=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            footer=cnst.ACTION_MODEL_FIELD_DEFAULT_FIGURE_TEXT,
            figure=dash_ag_grid(df_3_rows),
        ),
    ],
    controls=[
        vm.Button(
            id=cnst.ACTION_MODEL_FIELD_BUTTON_ID,
            actions=[
                vm.Action(
                    function=action_return_text(f"{cnst.ACTION_MODEL_FIELD_BUTTON_ID}"),
                    # Uses model fields (title, header...) as outputs instead of
                    # accessing the underlying Dash properties such as `children`.
                    outputs=[
                        # Graph
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}.title",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}.description",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}.header",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}.footer",
                        # AgGrid
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}.title",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}.description",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}.header",
                        f"{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}.footer",
                    ],
                )
            ],
        ),
    ],
)


action_ag_grid_underlying_id_shortcut_page = vm.Page(
    title=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_PAGE,
    id=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_PAGE,
    components=[
        vm.AgGrid(
            id=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_AG_GRID_ID,
            title="Click button to update the figure",
            figure=dash_ag_grid(df_3_rows),
            actions=[
                # Lambda action that takes `AgGrid.selectedRows` JSON and pastes it to the Card output.
                vm.Action(
                    # Uses the parent `vm.AgGrid.id` instead of the actual `dag.AgGrid` ID created by `dash_ag_grid`.
                    function=capture("action")(lambda x: str(x))(
                        f"{cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_AG_GRID_ID}.selectedRows"
                    ),
                    outputs=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_CARD_ID,
                )
            ],
        ),
        vm.Card(
            id=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_CARD_ID,
            text="Click ag-grid cell to update me",
        ),
    ],
)


action_control_shortcut_page = vm.Page(
    title=cnst.ACTION_CONTROL_SHORTCUT_PAGE,
    id=cnst.ACTION_CONTROL_SHORTCUT_PAGE,
    components=[
        vm.Graph(
            id=cnst.ACTION_CONTROL_SHORTCUT_GRAPH_ID,
            figure=px.scatter(df_3_rows, x="sepal_width", y="sepal_length", color="species"),
        ),
    ],
    controls=[
        vm.Filter(
            id=cnst.ACTION_CONTROL_SHORTCUT_FILTER_ID,
            column="species",
            selector=vm.RadioItems(
                options=["sepal_length", "petal_length"],
                value="sepal_length",
                # Works even without specifying the filter/parameter selector IDs or the `value` property.
                actions=vm.Action(
                    function=capture("action")(lambda x: x)(cnst.ACTION_CONTROL_SHORTCUT_FILTER_ID),
                    outputs=cnst.ACTION_CONTROL_SHORTCUT_PARAMETER_ID,
                ),
            ),
        ),
        vm.Parameter(
            id=cnst.ACTION_CONTROL_SHORTCUT_PARAMETER_ID,
            targets=[f"{cnst.ACTION_CONTROL_SHORTCUT_GRAPH_ID}.x"],
            selector=vm.RadioItems(
                value="sepal_length",
                options=["sepal_length", "petal_length"],
            ),
        ),
    ],
)
