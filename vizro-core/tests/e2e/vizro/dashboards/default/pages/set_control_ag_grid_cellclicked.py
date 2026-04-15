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

# Data for target ag_grid
# float values from 0.1 to 10, step 0.1, rounded to 1 decimal
cell_values = [round(x, 1) for x in np.arange(0.1, 10.1, 0.1)]
# str values from 1 to 100, step 1
row_values = [str(x) for x in range(0, 101)]
# Repeat lengths to match float_values length
column_list = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
column_values = (column_list * (len(cell_values) // len(column_list) + 1))[: len(cell_values)]
# Build DataFrame
df = pd.DataFrame(
    {"column_values": column_values, "cell_values": cell_values, "row_values": row_values[: len(cell_values)]}
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
            figure=dash_ag_grid(df),
        ),
    ],
    controls=[
        vm.Filter(
            id="set_control_column",
            column="column_values",
            targets=[cnst.SET_CONTROL_AG_GRID_CELL_CLICKED_TARGET_ID],
            selector=vm.Dropdown(),
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
