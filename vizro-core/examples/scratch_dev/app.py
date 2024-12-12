"""Dev app to try things out."""

from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm
from vizro.tables import dash_ag_grid
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv")
columnDefs = [
    {"field": "athlete", "headerName": "The full Name of the athlete"},
    {"field": "age", "headerName": "The number of Years since the athlete was born"},
    {"field": "country", "headerName": "The Country the athlete was born in"},
    {"field": "sport", "headerName": "The Sport the athlete participated in"},
    {"field": "total", "headerName": "The Total number of medals won by the athlete"},
]

defaultColDef = {
    "wrapHeaderText": True,
    "autoHeaderHeight": True,
}


# Test app -----------------
page = vm.Page(
    title="Page Title",
    components=[vm.AgGrid(figure=dash_ag_grid(df, columnDefs=columnDefs, defaultColDef=defaultColDef))],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
