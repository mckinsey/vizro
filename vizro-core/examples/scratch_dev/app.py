import vizro.models as vm
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro import Vizro
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")


@capture("ag_grid")
def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
    defaults = {
        "className": "ag-theme-quartz-dark ag-theme-vizro",
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "filterParams": {
                "buttons": ["apply", "reset"],
                "closeOnApply": True,
            },
            "flex": 1,
            "minWidth": 70,
        },
        # "style": {"height": "100%"},
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
    )


page = vm.Page(
    title="Example of a custom Dash AgGrid",
    components=[
        vm.AgGrid(
            id="custom_ag_grid",
            title="Custom Dash AgGrid",
            figure=my_custom_aggrid(
                data_frame=df, chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"]
            ),
        ),
    ],
    # controls=[
    #     vm.Parameter(
    #         targets=["custom_ag_grid.chosen_columns"],
    #         selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list()),
    #     )
    # ],
)

dashboard = vm.Dashboard(pages=[page])
if __name__ == "__main__":
    Vizro().build(dashboard).run()
