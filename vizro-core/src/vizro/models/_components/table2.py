import logging
from typing import Any, Dict, Literal

from dash import dash_table, html
from pydantic import Field

from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

logger = logging.getLogger(__name__)


class Table2(VizroBaseModel):
    """Creates a table utilizing dash_table.DataTable.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        data_frame (pd.DataFrame): Dataframe to be used for table.
        style_header (Dict[str, str]): Custom styling for header
        filter_action (str): 'native' to.
    """

    type: Literal["table2"] = "table2"
    data_frame: str = Field(..., description="Data frame to be visualized as table.")
    other_args: Dict[str, Any] = {}
    # filter_action: str = 'custom'
    # Todo:
    # Add parameters: style_table, style_cell, style_data, style_filter, style_header, style_cell_conditional,
    # style_data_conditional, style_filter_conditional, style_header_conditional, cols_to_remove

    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(self.data_frame, str):
            data_manager._add_component(self.id, self.data_frame)

    @classmethod
    def update_layout(self, template=None):
        pass

    @_log_call
    def build(self):
        data = data_manager._get_component_data(self.id)  # type: ignore

        table = dash_table.DataTable(
            data=data.to_dict("records"),
            columns=[{"name": i, "id": i} for i in data.columns],
            style_header=self.style_header,
            filter_action="custom",  # link: https://dash.plotly.com/datatable/filtering
            **other_args,
        )
        table_container = "table_container"

        return html.Div(table, className=table_container)
