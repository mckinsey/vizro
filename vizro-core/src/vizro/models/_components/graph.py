import logging
from typing import Dict, List, Literal

from dash import ClientsideFunction, Input, Output, State, clientside_callback, ctx, dcc
from dash.exceptions import MissingCallbackContextException
from plotly import graph_objects as go

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import pandas as pd

from vizro.actions._actions_utils import CallbackTriggerDict, _get_component_actions
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import ModelID
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Graph(VizroBaseModel):
    """Wrapper for `dcc.Graph` to visualize charts in dashboard.

    Args:
        type (Literal["graph"]): Defaults to `"graph"`.
        figure (CapturedCallable): Function that returns a graph.
            See `CapturedCallable`][vizro.models.types.CapturedCallable].
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["graph"] = "graph"
    figure: CapturedCallable = Field(
        ..., import_path="vizro.plotly.express", mode="graph", description="Function that returns a plotly `go.Figure`"
    )
    actions: List[Action] = []

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("figure")

    # Validators
    _set_actions = _action_validator_factory("clickData")
    _validate_callable = validator("figure", allow_reuse=True)(_process_callable_data_frame)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here to match Table and AgGrid and because we might want to use __call__ more in future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        kwargs.setdefault("data_frame", data_manager[self["data_frame"]].load())
        fig = self.figure(**kwargs)

        # Reduce `margin_t` if no title is provided and `margin_t` is not explicitly set.
        if fig.layout.margin.t is None and fig.layout.title.text is None:
            fig.update_layout(margin_t=24)

        # Increase `title_pad_t` if subtitle is provided and `title_pad_t` is not explicitly set.
        # Otherwise, the title is being cut off.
        if fig.layout.title.pad.t is None and fig.layout.title.text and "<br>" in fig.layout.title.text:
            fig.update_layout(title_pad_t=24)

        # Apply the template vizro_dark or vizro_light by setting fig.layout.template. This is exactly the same as
        # what the clientside update_graph_theme callback does, and it would be nice if we could just use that by
        # including Input(self.id, "figure") as input for that callback, but doing so leads to a small flicker between
        # completion of this serverside callback and starting that clientside callbacks.
        # Note that this does not fully set the template for plotly.express figures. Doing this post-fig creation update
        # relies on the fact that we have already set pio.templates.default before the self.figure call
        # above (but not with the _pio_templates_default context manager surrounding the above self.figure call,
        # since that would alter global state).
        # Possibly we should pass through the theme selector as an argument `template` in __call__ rather than fetching
        # it from ctx here. Remember that passing it as self.figure(template) is not helpful though, because custom
        # graph figures don't need a template argument, and the clientside them selector callback would override this
        # anyway.
        # Possibly we should enforce that __call__ can only be used within the context of a callback, but it's easy
        # to just swallow up the error here as it doesn't cause any problems.
        try:
            # At the moment theme_selector is always present so this if statement is redundant, but possibly in
            # future we'll have callbacks that do Graph.__call__() without theme_selector set.
            if "theme_selector" in ctx.args_grouping.get("external", {}):
                theme_selector_checked = ctx.args_grouping["external"]["theme_selector"]["value"]
                fig.layout.template = "vizro_light" if theme_selector_checked else "vizro_dark"
        except MissingCallbackContextException:
            logger.info("fig.update_layout called outside of callback context.")
        return fig

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
            raise KeyError(
                f"Missing 'custom_data' for the source graph with id {source_graph_id}. "
                "Ensure that `custom_data` is an argument of the custom chart function, and that the relevant entry is "
                "then passed to the underlying plotly function. When configuring the custom chart in `vm.Graph`, "
                "ensure that `custom_data` is passed. Example usage: "
                "vm.Graph(figure=my_custom_chart(df, custom_data=['column_1'], actions=[...]))"
            ) from exc

        customdata = ctd_click_data["value"]["points"][0]["customdata"]

        for action in source_graph_actions:
            if action.function._function.__name__ != "filter_interaction" or target not in action.function["targets"]:
                continue
            for custom_data_idx, column in enumerate(custom_data_columns):
                data_frame = data_frame[data_frame[column].isin([customdata[custom_data_idx]])]

        return data_frame

    @_log_call
    def build(self):
        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_graph_theme"),
            # Output here to ensure that the callback is only triggered if the graph exists on the currently open page.
            output=[Output(self.id, "figure")],
            inputs=[
                Input("theme_selector", "checked"),
                State("vizro_themes", "data"),
                State(self.id, "id"),
            ],
            prevent_initial_call=True,
        )

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
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
