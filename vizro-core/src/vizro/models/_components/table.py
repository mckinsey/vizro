import logging
from typing import Literal

import pandas as pd
from dash import State, dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

from vizro.actions._actions_utils import CallbackTriggerDict, _get_component_actions, _get_parent_vizro_model
from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Table(VizroBaseModel):
    """Wrapper for `dash_table.DataTable` to visualize tables in dashboard.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        figure (CapturedCallable): Function that returns a Dash DataTable. See [`vizro.tables`][vizro.tables].
        title (str): Title of the `Table`. Defaults to `""`.
        header (str): Markdown text positioned below the `Table.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information such as subtitles, descriptions, or additional context.
            Defaults to `""`.
        footer (str): Markdown text positioned below the `Table`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["table"] = "table"
    figure: CapturedCallable = Field(
        ..., import_path="vizro.tables", mode="table", description="Function that returns a `Dash DataTable`."
    )
    title: str = Field("", description="Title of the `Table`")
    header: str = Field(
        "",
        description="Markdown text positioned below the `Table.title`. Follows the CommonMark specification. Ideal for "
        "adding supplementary information such as subtitles, descriptions, or additional context.",
    )
    footer: str = Field(
        "",
        description="Markdown text positioned below the `Table`. Follows the CommonMark specification. Ideal for "
        "providing further details such as sources, disclaimers, or additional notes.",
    )
    actions: list[Action] = []

    _input_component_id: str = PrivateAttr()

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    set_actions = _action_validator_factory("active_cell")
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here since we want to use __call__ without arguments more in future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        if "data_frame" not in kwargs:
            kwargs["data_frame"] = data_manager[self["data_frame"]].load()
        figure = self.figure(**kwargs)
        figure.id = self._input_component_id
        return figure

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # See figure implementation for more details.
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
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: dict[str, CallbackTriggerDict]
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
            children=html.Div(
                children=[
                    html.H3(self.title, className="figure-title", id=f"{self.id}_title") if self.title else None,
                    dcc.Markdown(self.header, className="figure-header") if self.header else None,
                    # Refer to the vm.AgGrid build method for details on why we return the
                    # html.Div(id=self._input_component_id) instead of actual figure object
                    # with the original data_frame.
                    html.Div(
                        id=self.id,
                        children=[html.Div(id=self._input_component_id)],
                        className="table-container",
                    ),
                    dcc.Markdown(self.footer, className="figure-footer") if self.footer else None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
