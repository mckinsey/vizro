import logging
from typing import List, Literal

from dash import dcc
from plotly import graph_objects as go
from pydantic import Field, PrivateAttr, validator

import vizro.plotly.express as px
from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


def create_empty_fig(message: str) -> go.Figure:
    """Creates empty go.Figure object with a display message."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[None], y=[None], showlegend=False, hoverinfo="none"))
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{"text": message, "showarrow": False, "font": {"size": 16}}],
    )
    return fig


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
    _output_property: str = PrivateAttr("figure")

    # Re-used validators
    _set_actions = _action_validator_factory("clickData")
    _validate_callable = validator("figure", allow_reuse=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(str(self.id)))
        fig = self.figure(**kwargs)

        # Remove top margin if title is provided
        if fig.layout.title.text is None:
            fig.update_layout(margin_t=24)
        return fig

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Graph["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.figure[arg_name]

    @_log_call
    def build(self):
        return dcc.Loading(
            dcc.Graph(
                id=self.id,
                # We don't do self.__call__() until the Graph is actually built. This ensures that lazy data is not
                # loaded until the graph is first shown on the screen. At the moment, we eagerly run page.build() for
                # all pages in Dashboard.build in order to register all the callbacks in advance. In future this should
                # no longer be the case so that we achieve true lazy loading.
                figure=create_empty_fig(""),
                config={
                    "autosizable": True,
                    "frameMargins": 0,
                    "responsive": True,
                },
                className="chart_container",
            ),
            color="grey",
            parent_className="loading-container",
        )
