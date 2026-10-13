from dash_ag_grid import AgGrid

from vizro.models.types import capture


@capture("ag_grid")
def table_with_filtered_columns(data_frame=None, chosen_columns: list[str] | None = None):
    """Custom AG Grid with added logic to filter on chosen columns."""
    column_defs = [{"field": column} for column in chosen_columns]
    return AgGrid(rowData=data_frame.to_dict("records"), columnDefs=column_defs)
