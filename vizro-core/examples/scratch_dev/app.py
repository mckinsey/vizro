# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

df = px.data.iris()

page1 = vm.Page(
    title="LAYOUT_FLEX_WRAP_AND_AG_GRID",
    components=[
        vm.AgGrid(id=f"ag_grid_outer_id_{i}", figure=dash_ag_grid(df, id=f"ag_grid_inner_id_{i}")) for i in range(3)
    ],
    controls=[vm.Filter(column="species")],
)

page2 = vm.Page(
    title="LAYOUT_FLEX_GAP_AND_TABLE",
    components=[
        vm.Table(id=f"table_outer_id_{i}", figure=dash_data_table(df, id=f"table_inner_id_{i}")) for i in range(3)
    ],
    controls=[vm.Filter(column="species")],
)

page3 = vm.Page(
    title="cross_id",
    components=[
        vm.Table(figure=dash_data_table(df, id="qwert")),
        # TODO: See how configuration below raises an exception.
        # vm.AgGrid(figure=dash_ag_grid(df, id="qwert")),
    ],
    controls=[vm.Filter(column="species")],
)

page_4_ag_grid_error = vm.Page(
    title="AG_GRID_ERROR",
    components=[
        vm.AgGrid(
            id="duplicate-ag-grid-id",
            figure=dash_ag_grid(df, id="unique-ag-grid-id"),
            # TODO: See how configurations below raise an exception
            # figure=dash_ag_grid(df, id="duplicate-ag-grid-id"),
            # figure=dash_ag_grid(df, id="duplicate-table-id")
        )
    ],
    controls=[vm.Filter(column="species")],
)

page_5_table_error = vm.Page(
    title="TABLE_ERROR",
    components=[
        vm.Table(
            id="duplicate-table-id",
            figure=dash_data_table(df, id="unique-table-id"),
            # TODO: See how configurations below raise an exception.
            # figure=dash_data_table(df, id="duplicate-table-id")
            # figure=dash_data_table(df, id="duplicate-ag-grid-id"),
        )
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page1, page2, page3, page_4_ag_grid_error, page_5_table_error])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
