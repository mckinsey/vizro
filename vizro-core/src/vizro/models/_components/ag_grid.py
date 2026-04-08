import logging
from typing import Annotated, Any, Literal, TypeAlias, TypedDict, cast

import dash_ag_grid as dag
import pandas as pd
import vizro_dash_components as vdc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html, no_update
from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
)
from pydantic.json_schema import SkipJsonSchema

from vizro.actions import filter_interaction, set_control
from vizro.actions._actions_utils import CallbackTriggerDict, _get_triggered_model
from vizro.managers import data_manager, model_manager
from vizro.managers._model_manager import DuplicateIDError
from vizro.models import Tooltip, VizroBaseModel
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import (
    _log_call,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import (
    ActionsType,
    CapturedCallable,
    MultiValueType,
    SingleValueType,
    _IdProperty,
    _validate_captured_callable,
)

logger = logging.getLogger(__name__)

# A set of properties unique to dag.AgGrid (inner build object) that are not present in html.Div (outer build wrapper).
# Creates _action_outputs and _action_inputs for accessing inner dag.AgGrid properties via the outer vm.AgGrid ID.
# Example: "outer-ag-grid-id.cellClicked" is transformed to "inner-ag-grid-id.cellClicked".
DAG_AG_GRID_PROPERTIES = set(dag.AgGrid().available_properties) - set(html.Div().available_properties)

# User-friendly shortcuts for accessing `cellClicked` trigger fields since its structure differs from `selectedRows`.
CELL_CLICKED_MAPPING = {"cell": "value", "column": "colId", "row": "rowId"}


class CellClicked(TypedDict):
    value: Any
    colId: str
    rowId: Any
    rowIndex: int
    timestamp: int


SelectedRow: TypeAlias = dict[str, Any]


class Trigger(TypedDict):
    cellClicked: CellClicked
    selectedRows: list[SelectedRow]


class AgGrid(VizroBaseModel):
    """Wrapper for `dash_ag_grid.AgGrid` to visualize grids in dashboard.

    Abstract: Usage documentation
        [How to use an AgGrid](../user-guides/table.md/#ag-grid)

    """

    type: Literal["ag_grid"] = "ag_grid"
    figure: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(_process_callable_data_frame),
        Field(
            json_schema_extra={"mode": "ag_grid", "import_path": "vizro.tables"},
            description="Function that returns a `Dash AG Grid`.",
        ),
    ]
    title: str = Field(default="", description="Title of the `AgGrid`.")
    header: str = Field(
        default="",
        description="Markdown text positioned below the `AgGrid.title`. Follows the CommonMark specification. Ideal "
        "for adding supplementary information such as subtitles, descriptions, or additional context.",
    )
    footer: str = Field(
        "",
        description="Markdown text positioned below the `AgGrid`. Follows the CommonMark specification. Ideal for "
        "providing further details such as sources, disclaimers, or additional notes.",
    )
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description.""",
        ),
    ]
    actions: ActionsType = []
    _inner_component_id: str = PrivateAttr()

    _validate_figure = field_validator("figure", mode="before")(_validate_captured_callable)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    def model_post_init(self, context) -> None:
        super().model_post_init(context)
        self._inner_component_id = self.figure._arguments.get("id", f"__input_{self.id}")

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}_action_trigger.data"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.children",
            "figure": f"{self.id}.children",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"header": f"{self.id}_header.children"} if self.header else {}),
            **({"footer": f"{self.id}_footer.children"} if self.footer else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
            **{ag_grid_prop: f"{self._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {
            **{ag_grid_prop: f"{self._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }

    def _get_value_from_trigger(self, value: str, trigger: Trigger) -> MultiValueType | SingleValueType | None:
        """Extract values from the trigger that represents selected dag.AgGrid rows. Value is the name of the column.

        Example `trigger` structure: {
            "cellClicked": {"value": 1, "colId": "col_1", "rowId": 0, "rowIndex": 0},
            "selectedRows": [{"col_1": value_1, "col_2": value_2, ...}, {...}, ...]  # one dict per selected row.
        }

        Returns:
          - a single value (from `cellClicked`) or list of values (from `selectedRows`) or None  (signals reset).

        Raises:
          - ValueError if `value` column name can't be found.
        """
        if cell_clicked_value := CELL_CLICKED_MAPPING.get(value):
            if "cellClicked" in trigger:
                cell_clicked = cast(dict[str, Any], trigger["cellClicked"])
                # `cell_clicked_value` always present in the `cell_clicked`.
                return cell_clicked[cell_clicked_value]
            else:
                # Keep the target control unchanged if `cellClicked` is missing (e.g. checkbox row selection)
                return no_update

        selected_rows = trigger.get("selectedRows")

        # If `selectedRows` doesn't exist leave the target control unchanged except resetting it.
        if selected_rows is None:
            return no_update

        # Covers [] - Returning None signals a reset of control to its original value.
        if not selected_rows:
            return None

        try:
            # Use dict.fromkeys to remove duplicates while preserving order.
            return list(dict.fromkeys(row[value] for row in selected_rows))
        except KeyError:
            raise ValueError(
                f"Couldn't find value column name: `{value}` in trigger for `set_control` action. "
                f"This action was added to the AgGrid model with ID `{self.id}`. "
            )

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here since we want to use __call__ without arguments more in the future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        if "data_frame" not in kwargs:
            kwargs["data_frame"] = data_manager[self["data_frame"]].load()

        figure = self.figure(**kwargs)
        figure.id = self._inner_component_id

        figure.dashGridOptions.setdefault("getRowId", "params.data.sex")

        # Configure default grid interaction behavior based on the type of actions provided:
        all_set_control = all(isinstance(a, set_control) for a in self.actions)
        all_cell_clicked_actions = all_set_control and all(a.value in CELL_CLICKED_MAPPING for a in self.actions)
        all_selected_rows_actions = all_set_control and all(a.value not in CELL_CLICKED_MAPPING for a in self.actions)

        # No actions - Disable cell focus and row hover effects
        if not self.actions:
            figure.dashGridOptions.setdefault("suppressCellFocus", True)
            figure.dashGridOptions.setdefault("suppressRowHoverHighlight", True)
        # Any scenario except pure cell-click actions - Enable row selection UI
        elif not all_cell_clicked_actions:
            row_sel = figure.dashGridOptions.setdefault("rowSelection", {})
            row_sel.setdefault("mode", "multiRow")
            row_sel.setdefault("enableClickSelection", True)
            row_sel.setdefault("checkboxes", True)
            row_sel.setdefault("headerCheckbox", True)

            # If all actions are row-selection (no cell-click actions) - Suppress cell focus
            if all_selected_rows_actions:
                figure.dashGridOptions.setdefault("suppressCellFocus", True)

        return html.Div([figure, dcc.Store(id=f"{self._inner_component_id}_guard_actions_chain", data=True)])

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
            "cellClicked": State(component_id=self._inner_component_id, component_property="cellClicked"),
            "modelID": State(component_id=self.id, component_property="id"),  # required, to determine triggered model
        }

    def _filter_interaction(
        self, data_frame: pd.DataFrame, target: str, ctd_filter_interaction: dict[str, CallbackTriggerDict]
    ) -> pd.DataFrame:
        """Function to be carried out for `filter_interaction`."""
        # data_frame is the DF of the target, ie the data to be filtered, hence we cannot get the DF from this model
        ctd_cellClicked = ctd_filter_interaction["cellClicked"]
        if not ctd_cellClicked["value"]:
            return data_frame

        # ctd_active_cell["id"] represents the underlying table id, so we need to fetch its parent Vizro Table actions.
        source_table_actions = _get_triggered_model(ctd_cellClicked["id"]).actions

        for action in source_table_actions:
            # TODO-AV2 A 1: simplify this as in
            #  https://github.com/mckinsey/vizro/pull/1054/commits/f4c8c5b153f3a71b93c018e9f8c6f1b918ca52f6
            #  Potentially this function would move to the filter_interaction action. That will be removed so
            #  no need to worry too much if it doesn't work well, but we'll need to do something similar for the
            #  new interaction functionality anyway.
            if not isinstance(action, filter_interaction) or target not in action.targets:
                continue
            column = ctd_cellClicked["value"]["colId"]
            clicked_data = ctd_cellClicked["value"]["value"]
            data_frame = data_frame[data_frame[column].isin([clicked_data])]

        return data_frame

    @_log_call
    def pre_build(self):
        # Check if any other Vizro model or CapturedCallable has the same input component ID
        all_inner_component_ids = {  # type: ignore[var-annotated]
            model._inner_component_id
            for model in model_manager._get_models()
            if hasattr(model, "_inner_component_id") and model.id != self.id
        }

        if self._inner_component_id in set(model_manager) | all_inner_component_ids:
            raise DuplicateIDError(
                f"CapturedCallable with id={self._inner_component_id} has an id that is "
                "already in use by another Vizro model or CapturedCallable. "
                "CapturedCallables must have unique ids across the whole dashboard."
            )

    def build(self):
        clientside_callback(
            ClientsideFunction(namespace="ag_grid", function_name="update_ag_grid_action_trigger"),
            Output(f"{self.id}_action_trigger", "data"),
            Input(self._inner_component_id, "cellClicked"),
            Input(self._inner_component_id, "selectedRows"),
            prevent_initial_call=True,
            hidden=True,
        )

        description = self.description.build().children if self.description else [None]
        return dcc.Loading(
            children=html.Div(
                children=[
                    dcc.Store(id=f"{self.id}_action_trigger"),
                    html.H3([html.Span(self.title, id=f"{self.id}_title"), *description], className="figure-title")
                    if self.title
                    else None,
                    vdc.Markdown(self.header, className="figure-header", id=f"{self.id}_header")
                    if self.header
                    else None,
                    # The Div component with `id=self._inner_component_id` is rendered during the build phase.
                    # This placeholder component is quickly replaced by the actual AgGrid object, which is generated
                    # using a filtered data_frame and parameterized arguments as part of the on_page_load mechanism.
                    # To prevent pagination and persistence issues while maintaining a lightweight component initial
                    # load, this method now returns a html.Div object instead of the previous dag.AgGrid.
                    # The actual AgGrid is then rendered by the on_page_load mechanism.
                    # The `id=self._inner_component_id` is set to avoid the "Non-existing object" Dash exception.
                    html.Div(
                        id=self.id,
                        children=[html.Div(id=self._inner_component_id)],
                        className="table-container",
                    ),
                    vdc.Markdown(self.footer, className="figure-footer", id=f"{self.id}_footer")
                    if self.footer
                    else None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
