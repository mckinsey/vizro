import logging
from typing import Literal

import pandas as pd
from dash import State, dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator
from dash import ClientsideFunction, Input, Output, clientside_callback

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
        figure (CapturedCallable): Function that returns a Dash AgGrid. See [`vizro.tables`][vizro.tables].
        title (str): Title of the `AgGrid`. Defaults to `""`.
        header (str): Markdown text positioned below the `AgGrid.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information such as subtitles, descriptions, or additional context.
            Defaults to `""`.
        footer (str): Markdown text positioned below the `AgGrid`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["ag_grid"] = "ag_grid"
    figure: CapturedCallable = Field(
        ..., import_path="vizro.tables", mode="ag_grid", description="Function that returns a `Dash AG Grid`."
    )
    title: str = Field("", description="Title of the `AgGrid`")
    header: str = Field(
        "",
        description="Markdown text positioned below the `AgGrid.title`. Follows the CommonMark specification. Ideal "
        "for adding supplementary information such as subtitles, descriptions, or additional context.",
    )
    footer: str = Field(
        "",
        description="Markdown text positioned below the `AgGrid`. Follows the CommonMark specification. Ideal for "
        "providing further details such as sources, disclaimers, or additional notes.",
    )
    actions: list[Action] = []

    _input_component_id: str = PrivateAttr()

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    set_actions = _action_validator_factory("cellClicked")
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
            "cellClicked": State(component_id=self._input_component_id, component_property="cellClicked"),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: dict[str, CallbackTriggerDict]
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
        self._input_component_id = self.figure._arguments.get("id", f"__input_{self.id}")

    def build(self):
        clientside_callback(
            ClientsideFunction(namespace="dashboard", function_name="update_ag_grid_theme"),
            Output(self._input_component_id, "className"),
            Input("theme_selector", "checked"),
        )

        return dcc.Loading(
            children=html.Div(
                children=[
                    html.H3(self.title, className="figure-title", id=f"{self.id}_title") if self.title else None,
                    dcc.Markdown(self.header, className="figure-header") if self.header else None,
                    # The Div component with `id=self._input_component_id` is rendered during the build phase.
                    # This placeholder component is quickly replaced by the actual AgGrid object, which is generated
                    # using a filtered data_frame and parameterized arguments as part of the on_page_load mechanism.
                    # To prevent pagination and persistence issues while maintaining a lightweight component initial
                    # load, this method now returns a html.Div object instead of the previous dag.AgGrid.
                    # The actual AgGrid is then rendered by the on_page_load mechanism.
                    # The `id=self._input_component_id` is set to avoid the "Non-existing object" Dash exception.
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
