import logging
from typing import Annotated, Any, Literal, TypeAlias, TypedDict, cast

import dash_ag_grid as dag
import vizro_dash_components as vdc
from dash import ClientsideFunction, Input, Output, clientside_callback, dcc, html, no_update
from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
)
from pydantic.json_schema import SkipJsonSchema

from vizro.actions import set_controls
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
# In AG Grid mode these are exposed on the outer vm.Table id so actions can read/write inner grid properties.
# Example: "outer-table-id.cellClicked" is transformed to "inner-ag-grid-id.cellClicked".
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


class Table(VizroBaseModel):
    """Wrapper for a table figure to visualize tabular data in a dashboard.

    Renders an interactive `dash_ag_grid.AgGrid` from the `dash_ag_grid` figure provided.

    Abstract: Usage documentation
        [How to use tables](../user-guides/table.md)

    """

    type: Literal["table"] = "table"
    figure: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(_process_callable_data_frame),
        Field(
            json_schema_extra={"mode": "ag_grid", "import_path": "vizro.tables"},
            description="Function that returns a `Dash AG Grid`.",
        ),
    ]
    title: str = Field(default="", description="Title of the `Table`")
    header: str = Field(
        default="",
        description="Markdown text positioned below the `Table.title`. Follows the CommonMark specification. Ideal for "
        "adding supplementary information such as subtitles, descriptions, or additional context.",
    )
    footer: str = Field(
        default="",
        description="Markdown text positioned below the `Table`. Follows the CommonMark specification. Ideal for "
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
            # An AG Grid additionally exposes its inner grid properties (cellClicked, selectedRows, ...) as outputs.
            **{ag_grid_prop: f"{self._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        # An AG Grid exposes its inner properties (cellClicked, selectedRows, ...) as action inputs.
        return {ag_grid_prop: f"{self._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES}

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
                f"Couldn't find value column name: `{value}` in trigger for `set_controls` action. "
                f"This action was added to the {type(self).__name__} model with ID `{self.id}`. "
            )

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here since we want to use __call__ without arguments more in future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        if "data_frame" not in kwargs:
            kwargs["data_frame"] = data_manager[self["data_frame"]].load()
        figure = self.figure(**kwargs)
        figure.id = self._inner_component_id

        # Configure default grid interaction behavior based on the type of actions provided:
        all_set_controls = all(isinstance(a, set_controls) for a in self.actions)
        all_cell_clicked_actions = all_set_controls and all(a.value in CELL_CLICKED_MAPPING for a in self.actions)
        all_selected_rows_actions = all_set_controls and all(a.value not in CELL_CLICKED_MAPPING for a in self.actions)

        # Set dashGridOptions if not already set.
        figure.dashGridOptions = getattr(figure, "dashGridOptions", {})

        # Set default dashGridOptions.theme so custom charts use Vizro theming by default.
        figure.dashGridOptions.setdefault("theme", {"function": "vizroTheme(themeQuartz, agGrid)"})

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
        # An AG Grid needs a clientside callback + store to funnel cellClicked / selectedRows into a single trigger.
        clientside_callback(
            ClientsideFunction(namespace="ag_grid", function_name="update_ag_grid_action_trigger"),
            Output(f"{self.id}_action_trigger", "data"),
            Input(self._inner_component_id, "cellClicked"),
            Input(self._inner_component_id, "selectedRows"),
            prevent_initial_call=True,
            hidden=True,
        )

        description = self.description.build().children if self.description else [None]
        # The Div with `id=self._inner_component_id` is a lightweight placeholder rendered during build; the
        # on_page_load mechanism replaces it with the actual figure built from the (filtered) data_frame. This keeps
        # the initial load light and avoids pagination/persistence issues. `id=self._inner_component_id` is set to
        # avoid the "Non-existing object" Dash exception.
        children = [dcc.Store(id=f"{self.id}_action_trigger")]
        children += [
            html.H3([html.Span(self.title, id=f"{self.id}_title"), *description], className="figure-title")
            if self.title
            else None,
            vdc.Markdown(self.header, className="figure-header", id=f"{self.id}_header") if self.header else None,
            html.Div(
                id=self.id,
                children=[html.Div(id=self._inner_component_id)],
                className="table-container",
            ),
            vdc.Markdown(self.footer, className="figure-footer", id=f"{self.id}_footer") if self.footer else None,
        ]
        return dcc.Loading(
            children=html.Div(children=children, className="figure-container"),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
