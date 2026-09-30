# TODO[1.0.0]: delete this file - a Dash DataTable custom chart. Its only consumer, parameters_multi_page.py, moves
#  to a dash_ag_grid table (or drops these table components) when dash_data_table e2e coverage is removed.
from dash import dash_table

from vizro.models.types import capture


@capture("table")
def table_with_filtered_columns(data_frame=None, chosen_columns: list[str] | None = None):
    """Custom table with added logic to filter on chosen columns."""
    columns = [{"name": i, "id": i} for i in chosen_columns]
    defaults = {
        "style_as_list_view": True,
        "style_data": {"border_bottom": "1px solid var(--bs-border-color)", "height": "40px"},
        "style_header": {
            "border_bottom": "1px solid var(--bs-border-color-translucent)",
            "border_top": "1px solid var(--bs-body-bg)",
            "height": "32px",
        },
    }
    return dash_table.DataTable(data=data_frame.to_dict("records"), columns=columns, **defaults)
