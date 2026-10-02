"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import vizro.models as vm
import vizro.plotly.express as px
import yaml
from dash_ag_grid import AgGrid
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")
data_manager["gapminder_2007"] = df


@capture("ag_grid")
def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
    """Custom Dash AgGrid."""
    defaults = {
        "className": "ag-theme-vizro",
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
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
    )


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = vm.Dashboard(**dashboard)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
