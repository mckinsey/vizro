import logging
from typing import Dict, List, Literal

from dash import State, ctx, dcc
from dash.exceptions import MissingCallbackContextException
from plotly import graph_objects as go

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import pandas as pd

import vizro.plotly.express as px
from vizro import _themes as themes
from vizro.actions._actions_utils import CallbackTriggerDict, _get_component_actions
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _callable_mode_validator_factory, _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Graph(VizroBaseModel):
    """Wrapper for `dcc.Graph` to visualize charts in dashboard.

    Args:
        type (Literal["graph"]): Defaults to `"graph"`.
        figure (CapturedCallable): See [`CapturedCallable`][vizro.models.types.CapturedCallable].
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["graph"] = "graph"
    figure: CapturedCallable = Field(..., import_path=px)
    actions: List[Action] = []

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("figure")

    # Validators
    _set_actions = _action_validator_factory("clickData")
    _validate_callable_mode = _callable_mode_validator_factory("graph")
    _validate_callable = validator("figure", allow_reuse=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(str(self.id)))
        fig = self.figure(**kwargs)

        # Remove top margin if title is provided
        if fig.layout.title.text is None:
            fig.update_layout(margin_t=24)

        # Possibly we should enforce that __call__ can only be used within the context of a callback, but it's easy
        # to just swallow up the error here as it doesn't cause any problems.
        try:
            # At the moment theme_selector is always present so this if statement is redundant, but possibly in
            # future we'll have callbacks that do Graph.__call__() without theme_selector set.
            if "theme_selector" in ctx.args_grouping.get("external", {}):
                fig = self._update_theme(fig, ctx.args_grouping["external"]["theme_selector"]["value"])
        except MissingCallbackContextException:
            logger.info("fig.update_layout called outside of callback context.")
        return fig

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Graph["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    # Interaction methods
    @property
    def _filter_interaction_input(self):
        """Required properties when using pre-defined `filter_interaction`."""
        return {
            "clickData": State(component_id=self.id, component_property="clickData"),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: Dict[str, CallbackTriggerDict]
    ) -> pd.DataFrame:
        """Function to be carried out for pre-defined `filter_interaction`."""
        # data_frame is the DF of the target, ie the data to be filtered, hence we cannot get the DF from this model
        ctd_click_data = ctd_filter_interaction["clickData"]
        if not ctd_click_data["value"]:
            return data_frame

        source_graph_id: ModelID = ctd_click_data["id"]
        source_graph_actions = _get_component_actions(model_manager[source_graph_id])
        try:
            custom_data_columns = model_manager[source_graph_id]["custom_data"]
        except KeyError as exc:
            raise KeyError(f"No `custom_data` argument found for source graph with id {source_graph_id}.") from exc

        customdata = ctd_click_data["value"]["points"][0]["customdata"]

        for action in source_graph_actions:
            if action.function._function.__name__ != "filter_interaction" or target not in action.function["targets"]:
                continue
            for custom_data_idx, column in enumerate(custom_data_columns):
                data_frame = data_frame[data_frame[column].isin([customdata[custom_data_idx]])]

        return data_frame

    @_log_call
    def build(self):
        # The empty figure here is just a placeholder designed to be replaced by the actual figure when the filters
        # etc. are applied. It only appears on the screen for a brief instant, but we need to make sure it's
        # transparent and has no axes so it doesn't draw anything on the screen which would flicker away when the
        # graph callback is executed to make the dcc.Loading icon appear.
        return dcc.Loading(
            dcc.Graph(
                id=self.id,
                figure=go.Figure(
                    layout={
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "xaxis": {"visible": False},
                        "yaxis": {"visible": False},
                    }
                ),
                config={"autosizable": True, "frameMargins": 0, "responsive": True},
                className="chart_container",
            ),
            color="grey",
            parent_className="loading-container",
        )

    @staticmethod
    def _update_theme(fig: go.Figure, theme_selector: bool):
        # Basically the same as doing fig.update_layout(template="vizro_light/dark") but works for both the call in
        # self.__call__ and in the update_graph_theme callback.
        fig["layout"]["template"] = themes.light if theme_selector else themes.dark
        return fig
