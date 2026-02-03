import logging
import warnings
from contextlib import suppress
from typing import Annotated, Any, Literal, cast

import pandas as pd
from box import Box, BoxList
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html, set_props
from dash.exceptions import MissingCallbackContextException
from plotly import graph_objects as go
from pydantic import AfterValidator, BeforeValidator, Field, JsonValue, field_validator, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro._vizro_utils import _set_defaults_nested
from vizro.actions import filter_interaction
from vizro.actions._actions_utils import CallbackTriggerDict
from vizro.managers import data_manager, model_manager
from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    (
    ActionsType,

    CapturedCallable,

    ModelID,

    MultiValueType,
    _IdProperty,

    _validate_captured_callable,
    make_discriminated_union,
),
)

logger = logging.getLogger(__name__)


class Graph(VizroBaseModel):
    """Wrapper for `dcc.Graph` to visualize charts.

    Abstract: Usage documentation
        [How to use graphs](../user-guides/graph.md)

    Args:
        figure (CapturedCallable): Function that returns a graph. Either use
            [`vizro.plotly.express`](../user-guides/graph.md) or see
            [`CapturedCallable`][vizro.models.types.CapturedCallable].
        title (str): Title of the `Graph`. Defaults to `""`.
        header (str): Markdown text positioned below the `Graph.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information such as subtitles, descriptions, or additional context.
            Defaults to `""`.
        footer (str): Markdown text positioned below the `Graph`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        description (Tooltip | None): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
        extra (dict[str, Any]): Extra keyword arguments that are passed to `dcc.Graph` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/graph#graph-properties)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["graph"] = "graph"
    figure: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(_process_callable_data_frame),
        Field(
            json_schema_extra={"mode": "graph", "import_path": "vizro.plotly.express"},
            description="Function that returns a plotly `go.Figure`",
        ),
    ]
    title: str = Field(default="", description="Title of the `Graph`")
    header: str = Field(
        default="",
        description="Markdown text positioned below the `Graph.title`. Follows the CommonMark specification. Ideal for "
        "adding supplementary information such as subtitles, descriptions, or additional context.",
    )
    footer: str = Field(
        default="",
        description="Markdown text positioned below the `Graph`. Follows the CommonMark specification. Ideal for "
        "providing further details such as sources, disclaimers, or additional notes.",
    )
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        make_discriminated_union(Tooltip) | None,
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    actions: ActionsType = []
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dcc.Graph` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/graph#graph-properties)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    _validate_figure = field_validator("figure", mode="before")(_validate_captured_callable)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}_action_trigger.data"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.figure",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"header": f"{self.id}_header.children"} if self.header else {}),
            **({"footer": f"{self.id}_footer.children"} if self.footer else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    def _get_value_from_trigger(self, value: str, trigger: list[dict[str, JsonValue]]) -> MultiValueType | None:
        """Extract values from the trigger that represents clicked or selected Plotly graph points.

        Example `trigger` structure: [{"x": 1, customdata: ["value_1"], ...}, {...}, ...], one dict per selected point.

        Priority:
          1) If `value` matches a column name in self["custom_data"], take it as from customdata[index].
          2) Otherwise treat `value` as a Box lookup (e.g. "x", "customdata[0]").

        Notes:
          - Allows camelCase and snake_case value keys interchangeably (camel_killer_box=True).
          - Enables dot-style (e.g. value="key.subkey") access to nested dict values (box_dots=True).
          - Automatically creates missing keys as empty boxes instead of raising errors (default_box=True). This is done
            to avoid exceptions when the `trigger` has a key with a dot in it.

        Returns:
          - list of values (one per point) or None if no points selected (signals reset).

        Raises:
          - ValueError if `value` can't be found.
        """
        # Returning None signals a reset of control to its original value. No point selected when trigger is None
        # (unclicking a point) or its 'points' dictionary field is empty (selecting no points).
        if not trigger:
            return None

        # "default_box=True" is used to prevent exceptions that occur when a trigger key includes a dot.
        # The side effect is that `Box({})` will be returned later when `point[lookup]` does not exist.
        trigger_box = BoxList(trigger, camel_killer_box=True, box_dots=True, default_box=True)

        try:
            # First try to treat value as a column name. Unfortunately, the customdata returned in the trigger does
            # not contain column names (it's just a list) so we must look it up in the called function's `custom_data`
            # to find its numerical index in this list. This only works if a custom_data was provided in the graph
            # function call.
            index = self["custom_data"].index(value)
            lookup = f"customdata[{index}]"
        except (KeyError, ValueError):
            # Treat the value as a box lookup string, as https://github.com/cdgriffith/Box/wiki/Types-of-Boxes#box-dots
            # This works for e.g. value="x" or value="customdata[0]".
            lookup = value

        unique_points = set()
        try:
            for point in trigger_box:
                # Treat Box instance result as it's missing keys due to the `default_box=True`.
                if isinstance(val := point[lookup], Box):
                    raise KeyError

                # Certain grouped charts (e.g. pie charts) return custom data as a list of single-item lists
                # (e.g. [["setosa"], ["setosa"]]). Since all values are identical, flatten to a single value to avoid
                # returning a nested object.
                unique_points.add(val[0] if isinstance(val, list) else val)
        except (KeyError, IndexError, TypeError):
            raise ValueError(
                f"Couldn't find value `{value}` in trigger for `set_control` action. "
                f"This action was added to the Graph model with ID `{self.id}`. "
                "If you expected the value to come from custom data, add it in the figure's custom_data signature."
            )

        # The order of selected points is nondeterministic, so sort the values to provide consistent output.
        return sorted(unique_points)

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here since we want to use __call__ without arguments more in future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        if "data_frame" not in kwargs:
            kwargs["data_frame"] = data_manager[self["data_frame"]].load()
        fig = self.figure(**kwargs)
        fig = self._optimise_fig_layout_for_dashboard(fig)

        # Possibly we should enforce that __call__ can only be used within the context of a callback, but it's easy
        # to just swallow up the error here as it doesn't cause any problems.
        with suppress(MissingCallbackContextException):
            # After this callback has completed, the clientside update_graph_theme is triggered. In the case that
            # the theme selector has been set to the non-default theme, this would cause a flickering since the graph
            # with the wrong theme will be shown while the clientside callback runs. To avoid this we temporarily hide
            # the graph and then make it visible again in the clientside callback. Ideally this would be done using the
            # argument `running` on the clientside callback but this only exists for serverside callbacks, so we do it
            # manually.
            set_props(self.id, {"style": {"visibility": "hidden"}})

        # No "guard" component needed for vm.Graph. The reason is that vm.Graph has never been recreated after it's
        # built. Only that updates is its "figure" property after the build method.
        # Guard components are only for components (e.g. AgGrid, dynamic Filter) that get fully recreated.
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
        """Required properties when using `filter_interaction`."""
        return {
            "clickData": State(component_id=self.id, component_property="clickData"),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: dict[str, CallbackTriggerDict]
    ) -> pd.DataFrame:
        """Function to be carried out for `filter_interaction`."""
        # data_frame is the DF of the target, ie the data to be filtered, hence we cannot get the DF from this model
        ctd_click_data = ctd_filter_interaction["clickData"]
        if not ctd_click_data["value"]:
            return data_frame

        source_graph_id: ModelID = ctd_click_data["id"]
        source_graph = cast(Graph, model_manager[source_graph_id])

        try:
            custom_data_columns = source_graph["custom_data"]
        except KeyError as exc:
            raise KeyError(
                f"Missing 'custom_data' for the source graph with id {source_graph_id}. "
                "Ensure that `custom_data` is an argument of the custom chart function, and that the relevant entry is "
                "then passed to the underlying plotly function. When configuring the custom chart in `vm.Graph`, "
                "ensure that `custom_data` is passed. Example usage: "
                "vm.Graph(figure=my_custom_chart(df, custom_data=['column_1'], actions=[...]))"
            ) from exc

        customdata = ctd_click_data["value"]["points"][0]["customdata"]

        for action in source_graph.actions:
            # TODO-AV2 A 1: simplify this as in
            #  https://github.com/mckinsey/vizro/pull/1054/commits/f4c8c5b153f3a71b93c018e9f8c6f1b918ca52f6
            #  Potentially this function would move to the filter_interaction action. That will be removed so
            #  no need to worry too much if it doesn't work well, but we'll need to do something similar for the
            #  new interaction functionality anyway.
            if not isinstance(action, filter_interaction) or target not in action.targets:
                continue
            for custom_data_idx, column in enumerate(custom_data_columns):
                data_frame = data_frame[data_frame[column].isin([customdata[custom_data_idx]])]

        return data_frame

    def _optimise_fig_layout_for_dashboard(self, fig):
        """Post layout updates to visually enhance charts used inside dashboard."""
        # Determine if a title is present
        has_title = bool(fig.layout.title.text)

        # TODO: Check whether we should increase margins for all chart types in template_dashboard_overrides.py instead
        if any(isinstance(plotly_obj, go.Parcoords) for plotly_obj in fig.data):
            # Avoid hidden labels in Parcoords figures by increasing margins compared to dashboard defaults
            fig.update_layout(
                margin={
                    "t": fig.layout.margin.t or (92 if has_title else 40),
                    "l": fig.layout.margin.l or 36,
                    "b": fig.layout.margin.b or 24,
                },
            )

        if has_title and fig.layout.margin.t is None:
            # Reduce `margin_t` if not explicitly set.
            fig.update_layout(margin_t=64)

        if self.actions and not fig.layout.clickmode:
            # Set clickmode to "event+select" if there are actions defined and clickmode is not already set.
            fig.update_layout(clickmode="event+select")

        if not self.actions and fig.layout.modebar.remove is None:
            # Remove selection tools from modebar if there's no actions defined and the modebar.remove isn't already set
            fig.update_layout(modebar_remove=["select2d", "lasso2d"])

        return fig

    @_log_call
    def pre_build(self):
        try:
            self.figure["title"]
        except KeyError:
            pass
        else:
            warnings.warn(
                "Using the `title` argument in your Plotly chart function may cause misalignment with "
                "other component titles on the screen. To ensure consistent alignment, consider using "
                "`vm.Graph(title='Title', ...)`.",
                UserWarning,
            )

    @_log_call
    def build(self):
        clientside_callback(
            ClientsideFunction(namespace="dashboard", function_name="update_graph_theme"),
            output=[Output(self.id, "figure"), Output(self.id, "style")],
            inputs=[
                Input(self.id, "figure"),
                Input("theme-selector", "value"),
                State("vizro_themes", "data"),
            ],
            prevent_initial_call=True,
            hidden=True,
        )

        clientside_callback(
            ClientsideFunction(namespace="graph", function_name="update_graph_action_trigger"),
            Output(f"{self.id}_action_trigger", "data"),
            Input(self.id, "clickData"),
            Input(self.id, "selectedData"),
            State(self.id, "figure"),
            State(self.id, "id"),
            prevent_initial_call=True,
            hidden=True,
        )

        # The empty figure here is just a placeholder designed to be replaced by the actual figure when the filters
        # etc. are applied. It only appears on the screen for a brief instant, but we need to make sure it's
        # transparent and has no axes so it doesn't draw anything on the screen which would flicker away when the
        # graph callback is executed to make the dcc.Loading icon appear.
        description = self.description.build().children if self.description else [None]
        defaults = {
            "id": self.id,
            "figure": (
                go.Figure(
                    layout={
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "xaxis": {"visible": False},
                        "yaxis": {"visible": False},
                    }
                )
            ),
            "config": {
                "frameMargins": 0,
                "modeBarButtonsToRemove": ["toImage"],
            },
        }
        # While most components fully override defaults with values from `extra`,
        # for graph component we apply a merge to preserve our default values unless explicitly overridden.
        graph_defaults = _set_defaults_nested(self.extra, defaults)

        return dcc.Loading(
            children=html.Div(
                children=[
                    dcc.Store(id=f"{self.id}_action_trigger"),
                    html.H3([html.Span(self.title, id=f"{self.id}_title"), *description], className="figure-title")
                    if self.title
                    else None,
                    dcc.Markdown(self.header, className="figure-header", id=f"{self.id}_header")
                    if self.header
                    else None,
                    dcc.Graph(**graph_defaults),
                    dcc.Markdown(self.footer, className="figure-footer", id=f"{self.id}_footer")
                    if self.footer
                    else None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
