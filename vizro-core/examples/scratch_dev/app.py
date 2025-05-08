# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()

page1 = vm.Page(
    title="LAYOUT_FLEX_WRAP_AND_AG_GRID",
    layout=vm.Flex(wrap=True),
    components=[
        vm.AgGrid(id=f"outer_id_{i}", figure=dash_ag_grid(tips, id=f"inner_id_{i}", style={"width": 1000}))
        # vm.AgGrid(id=f"outer_id_{i}", figure=dash_ag_grid(tips, id=f"qwer", style={"width": 1000}))
        for i in range(3)
    ],
)

page2 = vm.Page(
    title="LAYOUT_FLEX_GAP_AND_TABLE",
    layout=vm.Flex(gap="40px"),
    # components=[vm.Table(figure=dash_data_table(tips, style_table={"width": "1000px"})) for i in range(3)],
    components=[vm.Table(figure=dash_data_table(tips, id="qwert", style_table={"width": "1000px"})) for i in range(3)],
)

dashboard = vm.Dashboard(pages=[page1, page2])


if __name__ == "__main__":
    Vizro().build(dashboard).run()

## TO CHECK: also for figure and/or Graph?
