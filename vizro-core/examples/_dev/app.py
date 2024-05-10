"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
from vizro import Vizro
from vizro.tables import dash_ag_grid

# DATA
data = {
    "this_is_a_really_long_column_name_0": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short_col_name": [4, 5, 6],
    "this_is_a_really_long_column_name_2": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short": [10, 11, 12],
    "this_is_a_really_long_column_name_4": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "this_is_a_really_long_column_name_6": [
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
        "sdfjalskdfnaksnfa;sldknfalksdnfl;kasdnfl;kasndflkasdf",
    ],
    "short4": [10, 11, 12],
    "this_is_a_really_long_column_name_7": [13, 14, 15],
}

df = pd.DataFrame(data)

# df = px.data.gapminder()

page = vm.Page(
    title="Example of a Dash AG Grid",
    components=[
        vm.AgGrid(
            title="Dash AG Grid",
            figure=dash_ag_grid(
                id="grid1",
                data_frame=df,
                defaultColDef={"flex": 1, "minWidth": 200},
                persistence=True,
                persisted_props=["filterModel", "columnSize"],  # ,persistence_type = "local" #columnSize="autoSize"#
            ),
        ),
    ],
    controls=[vm.Filter(column="this_is_a_really_long_column_name_0")],
)
page2 = vm.Page(
    title="Example of a Dash AG Grid 2",
    components=[
        vm.AgGrid(
            title="Dash AG Grid 2",
            figure=dash_ag_grid(
                id="grid2",
                data_frame=df,
                columnSize="autoSize",
                # , persistence=True, persisted_props=["filterModel","columnSize"]#,persistence_type = "local"
            ),
        ),
    ],
    # controls=[vm.Filter(column="continent")],
)
dashboard = vm.Dashboard(pages=[page, page2])

Vizro().build(dashboard).run()
