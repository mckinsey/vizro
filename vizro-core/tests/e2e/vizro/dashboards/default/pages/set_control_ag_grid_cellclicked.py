import e2e.vizro.constants as cnst
import numpy as np
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import set_control
from vizro.tables import dash_ag_grid

# Data for source ag_grid
iris = px.data.iris()
unique_species = iris["species"].unique()
iris_species_cycle = iris.copy()
iris_species_cycle["species"] = np.resize(unique_species, len(iris_species_cycle))

target_ag_grid_df = pd.DataFrame(
    {
        "column_values": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        "cell_values": [4.9, 3, 5.7, 0.4],
        "row_values": ["0", "1", "2", "3"],
    }
)

set_control_ag_grid_cellclicked = vm.Page(
    title=cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_PAGE,
    layout=vm.Grid(grid=[[0, 1], [2, 3], [4, 4]]),
    components=[
        vm.AgGrid(
            title="set_control.value=column",
            id=cnst.SET_CONTROL_AG_GRID_COLUMN_CLICKED_ID,
            figure=dash_ag_grid(iris_species_cycle),
            actions=set_control(control="set_control_column", value="column"),
        ),
        vm.AgGrid(
            title="set_control.value=cell",
            id=cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_ID,
            figure=dash_ag_grid(iris_species_cycle),
            actions=set_control(control="set_control_cell", value="cell"),
        ),
        vm.AgGrid(
            title="set_control.value=row",
            id=cnst.SET_CONTROL_AG_GRID_ROW_CLICKED_ID,
            figure=dash_ag_grid(iris_species_cycle),
            actions=set_control(control="set_control_row", value="row"),
        ),
        vm.AgGrid(
            title="set_control.value=mixed",
            id=cnst.SET_CONTROL_AG_GRID_MIXED_CLICKED_ID,
            figure=dash_ag_grid(iris_species_cycle),
            actions=[
                set_control(control="set_control_column", value="column"),
                set_control(control="set_control_cell", value="cell"),
            ],
        ),
        vm.AgGrid(
            title="AG Grid Cell Clicked Target",
            id=cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_TARGET_ID,
            figure=dash_ag_grid(target_ag_grid_df),
        ),
    ],
    controls=[
        vm.Filter(
            id="set_control_column",
            column="column_values",
            targets=[cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_TARGET_ID],
        ),
        vm.Filter(
            id="set_control_cell",
            column="cell_values",
            targets=[cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_TARGET_ID],
            selector=vm.Dropdown(),
        ),
        vm.Filter(
            id="set_control_row",
            column="row_values",
            targets=[cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_TARGET_ID],
            selector=vm.Dropdown(),
        ),
    ],
)
