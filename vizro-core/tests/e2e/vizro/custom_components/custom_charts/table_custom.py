from typing import Optional

from dash import dash_table

from vizro.models.types import capture


@capture("table")
def table_with_filtered_columns(data_frame=None, chosen_columns: Optional[list[str]] = None):
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
