import dash_ag_grid as dag
from dash import State

from vizro.models.types import capture


def dash_ag_grid(data_frame=None, **kwargs):
    """Custom AgGrid."""
    return dag.AgGrid(
        rowData=data_frame.to_dict("records"), columnDefs=[{"field": col} for col in data_frame.columns], **kwargs
    )


dash_ag_grid.action_info = {
    "filter_interaction_input": lambda x: {
        "cellClicked": State(component_id=x._callable_object_id, component_property="cellClicked"),
    }
}

dash_ag_grid = capture("table")(dash_ag_grid)