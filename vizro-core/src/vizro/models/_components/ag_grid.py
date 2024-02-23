import logging
from typing import Dict, List, Literal

import dash_ag_grid as dag
import pandas as pd
from dash import State, dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import vizro.tables as vt
from vizro.actions._actions_utils import CallbackTriggerDict, _get_component_actions, _get_parent_vizro_model
from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class AgGrid(VizroBaseModel):
    """Wrapper for `dash-ag-grid.AgGrid` to visualize grids in dashboard.

    Args:
        type (Literal["ag_grid"]): Defaults to `"ag_grid"`.
        figure (CapturedCallable): AgGrid like object to be displayed. For more information see:
            [`dash-ag-grid.AgGrid`](https://dash.plotly.com/dash-ag-grid).
        title (str): Title of the table. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["ag_grid"] = "ag_grid"
    figure: CapturedCallable = Field(..., import_path=vt, description="AgGrid to be visualized on dashboard")
    title: str = Field("", description="Title of the AgGrid")
    actions: List[Action] = []

    _callable_object_id: str = PrivateAttr()

    # Component properties for actions and interactions
    _output_property: str = PrivateAttr("children")

    # validator
    set_actions = _action_validator_factory("cellClicked")
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))
        return self.figure(**kwargs)

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # See table implementation for more details.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    # Interaction methods
    @property
    def _filter_interaction_input(self):
        """Required properties when using pre-defined `filter_interaction`."""
        return {
            "cellClicked": State(component_id=self._callable_object_id, component_property="cellClicked"),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: Dict[str, CallbackTriggerDict]
    ) -> pd.DataFrame:
        """Function to be carried out for pre-defined `filter_interaction`."""
        # data_frame is the DF of the target, ie the data to be filtered, hence we cannot get the DF from this model
        ctd_cellClicked = ctd_filter_interaction["cellClicked"]
        if not ctd_cellClicked["value"]:
            return data_frame

        # ctd_active_cell["id"] represents the underlying table id, so we need to fetch its parent Vizro Table actions.
        source_table_actions = _get_component_actions(_get_parent_vizro_model(ctd_cellClicked["id"]))

        for action in source_table_actions:
            if action.function._function.__name__ != "filter_interaction" or target not in action.function["targets"]:
                continue
            column = ctd_cellClicked["value"]["colId"]
            clicked_data = ctd_cellClicked["value"]["value"]
            data_frame = data_frame[data_frame[column].isin([clicked_data])]

        return data_frame

    @_log_call
    def pre_build(self):
        if self.actions:
            kwargs = self.figure._arguments.copy()

            # taken from table implementation - see there for details
            kwargs["data_frame"] = pd.DataFrame()
            underlying_aggrid_object = self.figure._function(**kwargs)

            if not hasattr(underlying_aggrid_object, "id"):
                raise ValueError(
                    "Underlying `AgGrid` callable has no attribute 'id'. To enable actions triggered by the `AgGrid`"
                    " a valid 'id' has to be provided to the `AgGrid` callable."
                )

            self._callable_object_id = underlying_aggrid_object.id

    def build(self):
        return dcc.Loading(
            html.Div(
                [
                    html.H3(self.title, className="table-title") if self.title else None,
                    html.Div(dag.AgGrid(**({"id": self._callable_object_id} if self.actions else {})), id=self.id),
                ],
                className="table-container",
                id=f"{self.id}_outer",
            ),
            color="grey",
            parent_className="loading-container",
        )
