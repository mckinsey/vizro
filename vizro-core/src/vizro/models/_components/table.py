import logging
from typing import List, Literal

import pandas as pd
from dash import dash_table, html
from pydantic import Field, PrivateAttr, validator

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
        table (CapturedCallable): Table like object to be displayed. Current choices include:
            [`dash_table.DataTable`](https://dash.plotly.com/datatable).
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["table"] = "table"
    table: CapturedCallable = Field(..., description="Table to be visualized on dashboard")  # ADD import path
    actions: List[Action] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("active_cell")
    _output_property: str = PrivateAttr("children")
    _callable_component: CapturedCallable = PrivateAttr()

    # validator
    set_actions = _action_validator_factory("active_cell")  # type: ignore[pydantic-field]
    _validate_callable = validator("table", allow_reuse=True, always=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))  # type: ignore[arg-type]
        return self.table(**kwargs)

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Table["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.table[arg_name]

    @_log_call
    def build(self):
        self._set_callable_component()
        return html.Div(
            dash_table.DataTable(pd.DataFrame().to_dict("records"), []), id=self.id
        )  # DOES NOT WORK IF NO CONTROL, CHECK WHY GRAPH WORKS

    def _set_callable_component(self):
        self._callable_component = self.table
