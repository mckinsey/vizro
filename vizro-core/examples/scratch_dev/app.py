"""Scratch demo app"""

import vizro.models as vm
from vizro import Vizro
import pandas as pd

from vizro.tables import dash_ag_grid

df = pd.DataFrame({"my_column": ["1", "2", 3, "B", True]})

page = vm.Page(
    title="Mixed options check",
    components=[vm.AgGrid(figure=dash_ag_grid(data_frame=df))],
    controls=[
        vm.Filter(
            column="my_column",
            selector=vm.Dropdown(
                options=["1", 2, {"label": "3.0", "value": 3}, "B", {"label": "True", "value": True}],
                value=["1", 2, "B", True],
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page],
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
