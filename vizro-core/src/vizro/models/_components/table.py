import logging
from typing import List, Literal, Optional

from dash import dash_table, dcc, html
from pydantic import Field, PrivateAttr, validator

import vizro.tables as vt
from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Table(VizroBaseModel):
    """Wrapper for table components to visualize in dashboard.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        figure (CapturedCallable): Table like object to be displayed. Current choices include:
            [`dash_table.DataTable`](https://dash.plotly.com/datatable).
        title (str): Title of the table. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["table"] = "table"
    figure: CapturedCallable = Field(..., import_path=vt, description="Table to be visualized on dashboard")
    title: Optional[str] = Field(None, description="Title of the table")
    actions: List[Action] = []

    # Component properties for actions and interactions
    _output_property: str = PrivateAttr("children")

    # validator
    set_actions = _action_validator_factory("active_cell")  # type: ignore[pydantic-field]
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))  # type: ignore[arg-type]
        return self.figure(**kwargs)

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Table["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    @_log_call
    def build(self):
        return dcc.Loading(
            html.Div(
                [
                    html.H3(self.title, className="table-title") if self.title else None,
                    html.Div(dash_table.DataTable(), id=self.id),
                ],
                className="table-container",
                id=f"{self.id}_outer",
            ),
            color="grey",
            parent_className="loading-container",
        )
