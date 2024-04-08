import logging
from typing import Dict, List, Literal

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
from vizro.models._components._components_utils import _callable_mode_validator_factory, _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Table(VizroBaseModel):
    """Wrapper for `dash_table.DataTable` to visualize tables in dashboard.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        figure (CapturedCallable): Table like object to be displayed. For more information see:
            [`dash_table.DataTable`](https://dash.plotly.com/datatable).
        title (str): Title of the table. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["table"] = "table"
    figure: CapturedCallable = Field(..., import_path=vt, description="Table to be visualized on dashboard")
    title: str = Field("", description="Title of the table")
    actions: List[Action] = []

    _input_component_id: str = PrivateAttr()

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    set_actions = _action_validator_factory("active_cell")
    _validate_callable_mode = _callable_mode_validator_factory("table")
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))
        figure = self.figure(**kwargs)
        figure.id = self._input_component_id
        return figure

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Table["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    # Interaction methods
    @property
    def _filter_interaction_input(self):
        """Required properties when using pre-defined `filter_interaction`."""
        return {
            "active_cell": State(component_id=self._input_component_id, component_property="active_cell"),
            "derived_viewport_data": State(
                component_id=self._input_component_id,
                component_property="derived_viewport_data",
            ),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: Dict[str, CallbackTriggerDict]
    ) -> pd.DataFrame:
        """Function to be carried out for pre-defined `filter_interaction`."""
        # data_frame is the DF of the target, ie the data to be filtered, hence we cannot get the DF from this model
        ctd_active_cell = ctd_filter_interaction["active_cell"]
        ctd_derived_viewport_data = ctd_filter_interaction["derived_viewport_data"]
        if not ctd_active_cell["value"] or not ctd_derived_viewport_data["value"]:
            return data_frame

        # ctd_active_cell["id"] represents the underlying table id, so we need to fetch its parent Vizro Table actions.
        source_table_actions = _get_component_actions(_get_parent_vizro_model(ctd_active_cell["id"]))

        for action in source_table_actions:
            if action.function._function.__name__ != "filter_interaction" or target not in action.function["targets"]:
                continue
            column = ctd_active_cell["value"]["column_id"]
            derived_viewport_data_row = ctd_active_cell["value"]["row"]
            clicked_data = ctd_derived_viewport_data["value"][derived_viewport_data_row][column]
            data_frame = data_frame[data_frame[column].isin([clicked_data])]

        return data_frame

    @_log_call
    def pre_build(self):
        self._input_component_id = self.figure._arguments.get("id", f"__input_{self.id}")

    def build(self):
        return dcc.Loading(
            html.Div(
                [
                    html.H3(self.title, className="table-title") if self.title else None,
                    html.Div(self.__call__(data_frame=pd.DataFrame()), id=self.id),
                ],
                className="table-container",
                id=f"{self.id}_outer",
            ),
            color="grey",
            parent_className="loading-container",
        )
