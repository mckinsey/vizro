"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import vizro.models as vm
import vizro.plotly.express as px
import yaml
from dash import dash_table
from dash_ag_grid import AgGrid
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")
data_manager["gapminder_2007"] = df


@capture("table")
def my_custom_table(chosen_columns: list[str], data_frame=None):
    """Custom Dash DataTable."""
    columns = [{"name": i, "id": i} for i in chosen_columns]
    defaults = {
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--bs-border-color)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--bs-border-color-translucent)",
            "border_top": "None",
            "height": "32px",
        },
    }
    return dash_table.DataTable(data=data_frame.to_dict("records"), columns=columns, **defaults)


@capture("ag_grid")
def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
    """Custom Dash AgGrid."""
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
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
    )


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = vm.Dashboard(**dashboard)


if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
