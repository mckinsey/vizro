import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid

import pandas as pd


# Define some sample data
data = {
    'this_is_a_really_long_column_name_0': [1, 2, 3],
    'short_col_name': [4, 5, 6],
    'this_is_a_really_long_column_name_2': [7, 8, 9],
    'short': [10, 11, 12],
    'this_is_a_really_long_column_name_4': [13, 14, 15]
}

# Create DataFrame
df = pd.DataFrame(data)

# df = px.data.gapminder()

page = vm.Page(
    title="Example of a Dash AG Grid",
    components=[
        vm.AgGrid(title="Dash AG Grid", figure=dash_ag_grid(data_frame=df,columnSize="autoSize")),
    ],
    # controls=[vm.Filter(column="continent")],
)
page2 = vm.Page(
    title="Example of a Dash AG Grid 2",
    components=[
        vm.AgGrid(title="Dash AG Grid 2", figure=dash_ag_grid(data_frame=df,columnSize="autoSize")),
    ],
    # controls=[vm.Filter(column="continent")],
)
dashboard = vm.Dashboard(pages=[page,page2])

Vizro().build(dashboard).run()