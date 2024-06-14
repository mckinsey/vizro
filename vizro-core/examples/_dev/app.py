"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df = px.data.gapminder()

# Vizro filter exporting Page --------------------------------------------
# Solution based on https://vizro.readthedocs.io/en/stable/pages/user-guides/actions/#export-data

page_one = vm.Page(
    title="Vizro filters exporting",
    layout=vm.Layout(grid=[[0]] * 5 + [[1]]),
    components=[
        vm.AgGrid(id="ag_grid_1", title="Equal Title One", figure=dash_ag_grid(data_frame=df)),
        vm.Button(text="Export data", actions=[vm.Action(function=export_data())]),
    ],
    controls=[vm.Filter(column="continent"), vm.Filter(column="year")],
)

# AgGrid filter exporting Page -------------------------------------------
# Solution based on https://dash.plotly.com/dash-ag-grid/export-data-csv


# More about Vizro Custom Actions -> https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-actions/
@capture("action")
def ag_grid_data_exporting():
    """Custom Action."""
    return True


page_two = vm.Page(
    title="AgGrid filters exporting",
    layout=vm.Layout(grid=[[0]] * 5 + [[1]]),  # grid = [[0], [0], [0], [0], [0], [1]]
    components=[
        vm.AgGrid(
            id="ag_grid_2",
            title="Equal Title One",
            figure=dash_ag_grid(
                # underlying_ag_grid_2 is the id of the AgGrid component on the client-side. It is used to reference
                # it's `exportDataAsCsv` property with the custom action below
                id="underlying_ag_grid_2",
                data_frame=df,
                csvExportParams={
                    "fileName": "ag_grid_2.csv",
                },
            ),
        ),
        vm.Button(
            id="button_2",
            text="Export data",
            actions=[vm.Action(function=ag_grid_data_exporting(), outputs=["underlying_ag_grid_2.exportDataAsCsv"])],
        ),
    ],
    controls=[vm.Filter(column="continent"), vm.Filter(column="year")],
)

dashboard = vm.Dashboard(pages=[page_one, page_two])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
