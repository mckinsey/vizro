import logging
from typing import List, Literal

from dash import dash_table, dcc, html
from pandas import DataFrame

try:
    from pydantic.v1 import Field, PrivateAttr, root_validator, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import vizro.tables as vt
from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _set_actions
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


def _get_table_type(figure): # this function can be applied also in pre-build
    kwargs = figure._arguments.copy()

    # This workaround is needed because the underlying table object requires a data_frame
    kwargs["data_frame"] = DataFrame()

    # The underlying table object is pre-built, so we can fetch its ID.
    underlying_table_object = figure._function(**kwargs)
    table_type = underlying_table_object.__class__.__name__
    return table_type


class Table(VizroBaseModel):
    """Wrapper for table components to visualize in dashboard.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        figure (CapturedCallable): Table like object to be displayed. Current choices include:
            [`dash_table.DataTable`](https://dash.plotly.com/datatable).
        title (str): Title of the table. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["table"] = "table"
    figure: CapturedCallable = Field(..., import_path=vt, description="Table to be visualized on dashboard")
    title: str = Field("", description="Title of the table")
    # foo: str = Field(None, exclude=True)
    actions: List[Action] = []

    _callable_object_id: str = PrivateAttr()
    _table_type: str = (
        PrivateAttr()
    )  # Ideally we would be able to use the populated content of this field in the `set_actions` validator.

    # Component properties for actions and interactions
    _output_property: str = PrivateAttr("children")

    # validator
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    @validator("actions")
    def set_actions(cls, v, values):
        table_type = _get_table_type(values["figure"])
        if table_type == "DataTable":
            return _set_actions(v, values, "active_cell")
        elif table_type == "AgGrid":
            return _set_actions(v, values, "cellClicked")
        else:
            raise ValueError(f"Table type {table_type} not supported.")

    # set_actions = _action_validator_factory("cellClicked")  # Need to make this sit with the captured callable

    # Approach similar to layout model - need to confirm if we can do without __init__ and populate at another time
    def __init__(self, **data):
        super().__init__(**data)
        self._table_type = _get_table_type(self.figure)

    @property
    def table_type(self):
        return self._table_type


    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))
        return self.figure(**kwargs)

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Table["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    @_log_call
    def pre_build(self):
        if self.actions:
            kwargs = self.figure._arguments.copy()

            # This workaround is needed because the underlying table object requires a data_frame
            kwargs["data_frame"] = DataFrame()

            # The underlying table object is pre-built, so we can fetch its ID.
            underlying_table_object = self.figure._function(**kwargs)
            table_type = underlying_table_object.__class__.__name__

            if not hasattr(underlying_table_object, "id"):
                raise ValueError(
                    "Underlying `Table` callable has no attribute 'id'. To enable actions triggered by the `Table`"
                    " a valid 'id' has to be provided to the `Table` callable."
                )

            self._callable_object_id = underlying_table_object.id
            self._table_type = table_type
            # Idea: fetch it from the functions attributes? Or just hard-code it here? Can check difference between AGGrid and dashtable because we call it already
            # Once we recognise, two ways to go: 1) slightly change model properties 2) inject dash dependencies,

    def build(self):
        return dcc.Loading(
            html.Div(
                [
                    html.H3(self.title, className="table-title") if self.title else None,
                    html.Div(
                        dash_table.DataTable(**({"id": self._callable_object_id} if self.actions else {})), id=self.id
                    ),
                ],
                className="table-container",
                id=f"{self.id}_outer",
            ),
            color="grey",
            parent_className="loading-container",
        )
