import e2e.vizro.constants as cnst
import pandas as pd

import vizro.models as vm
from vizro.tables import dash_ag_grid

data = {
    "user_id": range(1, 10),
    "name": ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian"],
    "age": [10, 20, 30, 15, 25, 35, 25, 35, 45],
    "signup_date": [
        "2023-01-01",
        "2023-01-02",
        "2023-01-03",
        "2023-01-04",
        "2023-01-05",
        "2023-01-06",
        "2023-01-07",
        "2023-01-08",
        "2023-01-09",
    ],
    "active": [True, False, True, False, True, False, True, False, True],
}
df = pd.DataFrame(data)

data.update({"active": [1, 0, 1, 0, 1, 0, 1, 0, 1]})
df_numeric = pd.DataFrame(data)


switch_control_page = vm.Page(
    title=cnst.SWITCH_CONTROL_PAGE,
    components=[
        vm.AgGrid(id=cnst.AG_GRID_INACTIVE, figure=dash_ag_grid(df)),
        vm.AgGrid(id=cnst.AG_GRID_ACTIVE, figure=dash_ag_grid(df_numeric)),
    ],
    controls=[
        vm.Filter(
            id=cnst.SWITCH_CONTROL_FALSE_ID,
            show_in_url=True,
            column="active",
            targets=[cnst.AG_GRID_INACTIVE],
            selector=vm.Switch(
                value=False,
                title="Show active accounts",
                description="This is a description for the new switch selector",
            ),
        ),
        vm.Filter(
            id=cnst.SWITCH_CONTROL_FALSE_DEFAULT_ID, show_in_url=True, column="active", targets=[cnst.AG_GRID_INACTIVE]
        ),
        vm.Filter(
            id=cnst.SWITCH_CONTROL_TRUE_ID,
            show_in_url=True,
            column="active",
            targets=[cnst.AG_GRID_ACTIVE],
            selector=vm.Switch(
                value=True,
                title="Show inactive accounts",
                description=vm.Tooltip(
                    text="This is a description for the new switch selector", icon=cnst.CONTAINER_TOOLTIP_ICON
                ),
            ),
        ),
    ],
)
