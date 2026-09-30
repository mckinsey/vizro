"""Unit tests for vizro.models.Table."""

import re
import warnings

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pytest
import vizro_dash_components as vdc
from asserts import STRIP_ALL, assert_component_equal
from dash import dcc, html, no_update
from pydantic import ValidationError

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.managers._model_manager import DuplicateIDError
from vizro.models._action._action import Action
from vizro.models._components.table import DAG_AG_GRID_PROPERTIES
from vizro.models.types import capture
from vizro.tables import dash_ag_grid, dash_data_table

# The Dash DataTable backing is deprecated in favor of a `dash_ag_grid` figure. Existing tests below keep exercising
# it; test_dash_data_table_backing_deprecated asserts the deprecation warning itself.
# TODO[1.0.0]: when the Dash DataTable backing is removed, delete the DataTable-only classes/tests in this module
#  (test_dash_data_table_backing_deprecated, TestTableInstantiation, TestDunderMethodsTable, TestProcessTableDataFrame,
#  TestPreBuildTable, TestBuildTable, the dash_table_* fixtures and this pytestmark). The AG-Grid classes at the end of
#  this module (TestTableAgGrid* and TestTableAgGridBuild etc.) survive as the canonical `Table` coverage.
pytestmark = pytest.mark.filterwarnings("ignore:The Dash DataTable backing:FutureWarning")


def test_dash_data_table_backing_deprecated():
    with pytest.warns(FutureWarning, match="The Dash DataTable backing"):
        vm.Table(figure=dash_data_table(data_frame=px.data.gapminder()))


class TestTableAgGrid:
    """`vm.Table` with a `dash_ag_grid` figure — the recommended, warning-free table."""

    def test_ag_grid_figure_is_warning_free(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", FutureWarning)
            table = vm.Table(figure=dash_ag_grid(data_frame=px.data.gapminder()))
        assert table._is_ag_grid is True

    def test_ag_grid_action_triggers(self):
        table = vm.Table(id="ag_table", figure=dash_ag_grid(data_frame=px.data.gapminder()))
        assert table._action_triggers == {"__default__": "ag_table_action_trigger.data"}

    def test_ag_grid_exposes_inner_properties_as_action_io(self):
        table = vm.Table(id="ag_table", figure=dash_ag_grid(data_frame=px.data.gapminder()))
        assert "cellClicked" in table._action_inputs
        assert "cellClicked" in table._action_outputs

    def test_undefined_dash_ag_grid_figure_is_recognized_as_ag_grid(self):
        # On the `allow_undefined_captured_callable` path (used by vizro-mcp for not-yet-importable configs) the
        # figure's `_mode` is unresolved, so `_is_ag_grid` must fall back to the `dash_ag_grid` function name. Otherwise
        # the figure is misclassified as a Dash DataTable and rejected as a `set_controls` source, breaking the promise
        # that `vm.Table(figure=dash_ag_grid(...))` is functionally identical to the deprecated `vm.AgGrid`.
        table = vm.Table.model_validate(
            {"figure": {"_target_": "dash_ag_grid", "data_frame": "gapminder"}},
            context={"allow_undefined_captured_callable": ["dash_ag_grid"]},
        )
        assert table.figure._mode is None
        assert table._is_ag_grid is True

    def test_undefined_dash_data_table_figure_is_not_ag_grid(self):
        # The deprecated Dash DataTable backing must stay classified as a DataTable on the undefined path too.
        table = vm.Table.model_validate(
            {"figure": {"_target_": "dash_data_table", "data_frame": "gapminder"}},
            context={"allow_undefined_captured_callable": ["dash_data_table"]},
        )
        assert table.figure._mode is None
        assert table._is_ag_grid is False


@pytest.fixture
def dash_table_with_arguments():
    return dash_data_table(data_frame=px.data.gapminder(), style_header={"border": "1px solid green"})


@pytest.fixture
def dash_table_with_str_dataframe():
    return dash_data_table(data_frame="gapminder")


class TestTableInstantiation:
    def test_create_graph_mandatory_only(self, standard_dash_table):
        table = vm.Table(figure=standard_dash_table)

        assert hasattr(table, "id")
        assert table.type == "table"
        assert table.figure == standard_dash_table
        assert table.actions == []
        assert table.title == ""
        assert table.header == ""
        assert table.footer == ""
        assert hasattr(table, "_inner_component_id")
        assert table._action_triggers == {"__default__": f"{table._inner_component_id}.active_cell"}
        assert table._action_outputs == {
            "__default__": f"{table.id}.children",
            "figure": f"{table.id}.children",
        }

    def test_create_table_mandatory_and_optional(self, dash_data_table_with_id):
        table = vm.Table(
            id="table-id",
            figure=dash_data_table_with_id,
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            header="Header",
            footer="Footer",
        )

        assert table.id == "table-id"
        assert table.type == "table"
        assert table.figure == dash_data_table_with_id
        assert table.actions == []
        assert table.title == "Title"
        assert table.header == "Header"
        assert table.footer == "Footer"
        assert isinstance(table.description, vm.Tooltip)
        assert table._inner_component_id == "underlying_table_id"
        assert table._action_triggers == {"__default__": "underlying_table_id.active_cell"}
        assert table._action_outputs == {
            "__default__": "table-id.children",
            "figure": "table-id.children",
            "title": "table-id_title.children",
            "header": "table-id_header.children",
            "footer": "table-id_footer.children",
            "description": "tooltip-id-text.children",
        }

    def test_table_filter_interaction_attributes(self, dash_data_table_with_id):
        table = vm.Table(figure=dash_data_table_with_id, title="Gapminder")
        assert hasattr(table, "_filter_interaction_input")
        assert "modelID" in table._filter_interaction_input

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Table()

    def test_captured_callable_invalid(self, standard_go_chart):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "Invalid CapturedCallable. Supply a function imported from vizro.tables or "
                "defined with decorator @capture('ag_grid') or @capture('table')."
            ),
        ):
            vm.Table(figure=standard_go_chart)

    def test_is_model_inheritable(self, standard_dash_table):
        class MyTable(vm.Table):
            pass

        my_table = MyTable(figure=standard_dash_table)

        assert hasattr(my_table, "id")
        assert my_table.type == "table"
        assert my_table.figure == standard_dash_table
        assert my_table.actions == []

    def test_table_trigger(self, dash_data_table_with_id, identity_action_function):
        table = vm.Table(figure=dash_data_table_with_id, actions=[Action(function=identity_action_function())])
        [action] = table.actions
        assert action._trigger == "underlying_table_id.active_cell"


class TestDunderMethodsTable:
    def test_getitem_known_args(self, dash_table_with_arguments):
        table = vm.Table(figure=dash_table_with_arguments)
        assert table["style_header"] == {"border": "1px solid green"}
        assert table["type"] == "table"

    def test_getitem_unknown_args(self, standard_dash_table):
        table = vm.Table(figure=standard_dash_table)
        with pytest.raises(KeyError):
            table["unknown_args"]

    def test_underlying_id_is_auto_generated(self, standard_dash_table):
        table = vm.Table(id="table", figure=standard_dash_table)
        table.pre_build()
        # table() is the same as table.__call__()
        assert "__input_table" in table()

    def test_underlying_id_is_provided(self, dash_data_table_with_id):
        table = vm.Table(figure=dash_data_table_with_id)
        table.pre_build()
        # table() is the same as table.__call__()
        assert "underlying_table_id" in table()


class TestProcessTableDataFrame:
    # Testing at this low implementation level as mocking callback contexts skips checking for creation of these objects
    def test_process_figure_data_frame_str_df(self, dash_table_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        table = vm.Table(id="table", figure=dash_table_with_str_dataframe)
        assert data_manager[table["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, standard_dash_table, gapminder):
        table = vm.Table(id="table", figure=standard_dash_table)
        assert data_manager[table["data_frame"]].load().equals(gapminder)


class TestPreBuildTable:
    def test_pre_build_no_underlying_table_id(self, standard_dash_table):
        table = vm.Table(id="text_table", figure=standard_dash_table)
        table.pre_build()

        assert table._inner_component_id == "__input_text_table"

    def test_pre_build_underlying_table_id(self, dash_data_table_with_id):
        table = vm.Table(id="text_table", figure=dash_data_table_with_id)
        table.pre_build()

        assert table._inner_component_id == "underlying_table_id"

    def test_pre_build_duplicate_input_table_id(self):
        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Test Page",
                    components=[
                        vm.Table(figure=dash_data_table(id="duplicate_table_id", data_frame=px.data.gapminder())),
                        vm.Table(figure=dash_data_table(id="duplicate_table_id", data_frame=px.data.gapminder())),
                    ],
                )
            ]
        )
        with pytest.raises(
            DuplicateIDError,
            match="CapturedCallable with id=duplicate_table_id has an id that is ",
        ):
            Vizro().build(dashboard)

    def test_pre_build_duplicate_input_table_id_and_button_id(self):
        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Test Page",
                    components=[
                        vm.Table(figure=dash_data_table(id="duplicate_table_id", data_frame=px.data.gapminder())),
                        vm.Button(id="duplicate_table_id"),
                    ],
                )
            ]
        )
        with pytest.raises(
            DuplicateIDError,
            match="CapturedCallable with id=duplicate_table_id has an id that is ",
        ):
            Vizro().build(dashboard)


class TestBuildTable:
    def test_table_build_mandatory_only(self, standard_dash_table, gapminder):
        table = vm.Table(figure=standard_dash_table)
        table.pre_build()
        table = table.build()
        expected_table = dcc.Loading(
            html.Div(
                children=[
                    None,
                    None,
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table, keys_to_strip={"id"})

    @pytest.mark.parametrize(
        "table, underlying_id_expected",
        [
            ("dash_data_table_with_id", "underlying_table_id"),
            ("standard_dash_table", "__input_text_table"),
        ],
    )
    def test_table_build_with_and_without_underlying_id(self, table, underlying_id_expected, request):
        table = vm.Table(id="text_table", figure=request.getfixturevalue(table))
        table.pre_build()
        table = table.build()

        expected_table = dcc.Loading(
            html.Div(
                children=[
                    None,
                    None,
                    html.Div(
                        id="text_table",
                        children=[html.Div(id=underlying_id_expected)],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table)

    def test_table_build_title_header_footer(self, standard_dash_table):
        table = vm.Table(
            figure=standard_dash_table, title="Title", header="""#### Subtitle""", footer="""SOURCE: **DATA**"""
        )
        table.pre_build()
        table = table.build()
        expected_table = dcc.Loading(
            html.Div(
                children=[
                    html.H3([html.Span("Title"), None], className="figure-title"),
                    vdc.Markdown("""#### Subtitle""", className="figure-header"),
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    vdc.Markdown("""SOURCE: **DATA**""", className="figure-footer"),
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table, keys_to_strip={"id"})

    def test_table_build_title_info_icon(self, standard_dash_table):
        table = vm.Table(
            figure=standard_dash_table,
            title="Title",
            description=vm.Tooltip(text="Tooltip test", icon="Info", id="info"),
        )
        table.pre_build()
        table = table.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=vdc.Markdown("Tooltip test", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]
        expected_table = dcc.Loading(
            html.Div(
                children=[
                    html.H3([html.Span("Title"), *expected_description], className="figure-title"),
                    None,
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table, keys_to_strip={"id"})


# ==============================================================================================================
# AG-Grid coverage for `vm.Table(figure=dash_ag_grid(...))` — the recommended, surviving table backing.
#
# These classes mirror the behavioral coverage that historically lived only in test_legacy_ag_grid.py (against the
# deprecated `vm.AgGrid` model). AG-Grid figures emit no deprecation warning, so these tests run warning-free. When the
# Dash DataTable backing and the `AgGrid` alias are removed in 1.0.0, test_legacy_ag_grid.py and the DataTable-only
# classes above are deleted, and these classes remain as the canonical `Table` coverage.
# ==============================================================================================================
class TestTableAgGridInstantiation:
    def test_create_mandatory_only(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)

        assert hasattr(table, "id")
        assert table.type == "table"
        assert table.figure == standard_ag_grid
        assert table.actions == []
        assert table.title == ""
        assert table.header == ""
        assert table.footer == ""
        assert table.description is None
        assert hasattr(table, "_inner_component_id")
        assert table._action_triggers == {"__default__": f"{table.id}_action_trigger.data"}
        assert table._action_outputs == {
            "__default__": f"{table.id}.children",
            "figure": f"{table.id}.children",
            **{ag_grid_prop: f"{table._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }
        assert table._action_inputs == {
            **{ag_grid_prop: f"{table._inner_component_id}.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }

    def test_create_mandatory_and_optional(self, ag_grid_with_id):
        table = vm.Table(
            id="ag-grid-id",
            figure=ag_grid_with_id,
            title="Title",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            header="Header",
            footer="Footer",
        )

        assert table.id == "ag-grid-id"
        assert table.type == "table"
        assert table.figure == ag_grid_with_id
        assert table.actions == []
        assert table.title == "Title"
        assert table.header == "Header"
        assert table.footer == "Footer"
        assert isinstance(table.description, vm.Tooltip)
        assert table._inner_component_id == "underlying_ag_grid_id"
        assert table._action_triggers == {"__default__": "ag-grid-id_action_trigger.data"}
        assert table._action_outputs == {
            "__default__": "ag-grid-id.children",
            "figure": "ag-grid-id.children",
            "title": "ag-grid-id_title.children",
            "header": "ag-grid-id_header.children",
            "footer": "ag-grid-id_footer.children",
            "description": "tooltip-id-text.children",
            **{ag_grid_prop: f"underlying_ag_grid_id.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }
        assert table._action_inputs == {
            **{ag_grid_prop: f"underlying_ag_grid_id.{ag_grid_prop}" for ag_grid_prop in DAG_AG_GRID_PROPERTIES},
        }

    def test_filter_interaction_attributes(self, ag_grid_with_id):
        table = vm.Table(figure=ag_grid_with_id, title="Gapminder")
        assert hasattr(table, "_filter_interaction_input")
        assert "modelID" in table._filter_interaction_input

    def test_table_trigger(self, ag_grid_with_id, identity_action_function):
        table = vm.Table(figure=ag_grid_with_id, actions=[Action(function=identity_action_function())])
        [action] = table.actions
        assert action._trigger == f"{table.id}_action_trigger.data"


class TestTableAgGridGetValueFromTrigger:
    """Tests the `_get_value_from_trigger` method for a `dash_ag_grid`-backed `Table`."""

    def test_selected_rows_no_trigger_data(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(value="continent", trigger={})

        assert value is no_update

    def test_clicked_cell_no_trigger_data(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(value="column", trigger={})

        assert value is no_update

    def test_empty_selected_rows_trigger_data(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(value="continent", trigger={"selectedRows": []})

        assert value is None

    def test_selected_rows_value_valid(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(
            value="continent", trigger={"selectedRows": [{"country": "France", "continent": "Europe", "year": 2007}]}
        )

        assert value == ["Europe"]

    def test_clicked_cell_value_valid(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(value="column", trigger={"cellClicked": {"colId": "Europe"}})

        assert value == "Europe"

    @pytest.mark.parametrize(
        "trigger, expected_result",
        [
            ({"selectedRows": [{"continent": "Europe"}]}, ["Europe"]),
            ({"selectedRows": [{"continent": "Europe"}, {"continent": "Europe"}]}, ["Europe"]),
            # `_get_value_from_trigger` ensures uniqueness but preserves the order
            (
                {"selectedRows": [{"continent": "Europe"}, {"continent": "Europe"}, {"continent": "Asia"}]},
                ["Europe", "Asia"],
            ),
        ],
    )
    def test_selected_rows_uniqueness_and_order_multiple_points_selected(
        self,
        standard_ag_grid,
        trigger,
        expected_result,
    ):
        table = vm.Table(figure=standard_ag_grid)
        value = table._get_value_from_trigger(value="continent", trigger=trigger)

        assert value == expected_result

    def test_value_unknown(self, standard_ag_grid):
        table = vm.Table(id="ag_grid_id", figure=standard_ag_grid)

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Couldn't find value column name: `unknown` in trigger for `set_controls` action. "
                "This action was added to the Table model with ID `ag_grid_id`. "
            ),
        ):
            table._get_value_from_trigger(
                value="unknown",
                trigger={"selectedRows": [{"country": "France", "continent": "Europe", "year": 2007}]},
            )


class TestTableAgGridGetItem:
    def test_getitem_known_args(self, dash_ag_grid_with_arguments):
        table = vm.Table(figure=dash_ag_grid_with_arguments)
        assert table["defaultColDef"] == {"resizable": False, "sortable": False}
        assert table["type"] == "table"

    def test_getitem_unknown_args(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        with pytest.raises(KeyError):
            table["unknown_args"]


class TestTableAgGridProcessDataFrame:
    def test_process_figure_data_frame_str_df(self, dash_ag_grid_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        table = vm.Table(id="ag_grid", figure=dash_ag_grid_with_str_dataframe)
        assert data_manager[table["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, standard_ag_grid, gapminder):
        table = vm.Table(id="ag_grid", figure=standard_ag_grid)
        assert data_manager[table["data_frame"]].load().equals(gapminder)


class TestTableAgGridCall:
    def test_call_underlying_id_is_auto_generated(self, standard_ag_grid):
        table = vm.Table(id="ag_grid_id", figure=standard_ag_grid)
        table.pre_build()
        # table() is the same as table.__call__()
        result_table = table()

        # Assert that Table.__call__() is the html.Div
        assert_component_equal(result_table, html.Div(), keys_to_strip=STRIP_ALL)

        # Assert that html.Div children contains the underlying AgGrid component and guard actions chain store component
        [result_table_grid, result_table_guard_store] = result_table.children

        assert result_table_grid.id == "__input_ag_grid_id"
        assert_component_equal(result_table_grid, dag.AgGrid(), keys_to_strip=STRIP_ALL)
        assert_component_equal(
            result_table_guard_store,
            dcc.Store(id="__input_ag_grid_id_guard_actions_chain", data=True),
        )

    def test_call_underlying_id_is_provided(self, ag_grid_with_id):
        table = vm.Table(id="ag_grid_id", figure=ag_grid_with_id)
        table.pre_build()
        # table() is the same as table.__call__()
        result_table = table()

        # Assert that Table.__call__() is the html.Div
        assert_component_equal(result_table, html.Div(), keys_to_strip=STRIP_ALL)

        # Assert that html.Div children contains the underlying AgGrid component and guard actions chain store component
        [result_table_grid, result_table_guard_store] = result_table.children

        assert result_table_grid.id == "underlying_ag_grid_id"
        assert_component_equal(result_table_grid, dag.AgGrid(), keys_to_strip=STRIP_ALL)
        assert_component_equal(
            result_table_guard_store,
            dcc.Store(id="underlying_ag_grid_id_guard_actions_chain", data=True),
        )

    @pytest.mark.parametrize(
        "table_actions, row_selection_input, expected_row_selection",
        [
            ([], {}, {}),
            ([], {"mode": "singleRow"}, {"mode": "singleRow"}),
            (
                va.set_controls(controls=["control_id"], value="continent"),
                {},
                {"mode": "multiRow", "checkboxes": True, "headerCheckbox": True, "enableClickSelection": True},
            ),
            (
                va.set_controls(controls=["control_id"], value="continent"),
                {"mode": "singleRow"},
                {"mode": "singleRow", "checkboxes": True, "headerCheckbox": True, "enableClickSelection": True},
            ),
        ],
    )
    def test_call_row_selection_when_set_controls_defined(
        self,
        table_actions,
        row_selection_input,
        expected_row_selection,
    ):
        table = vm.Table(
            figure=dash_ag_grid(data_frame=px.data.gapminder(), dashGridOptions={"rowSelection": row_selection_input}),
            actions=table_actions,
        )
        table.pre_build()
        # table() is the same as table.__call__()
        result_table = table()

        # Extract dag.AgGrid
        result_table_grid = result_table.children[0]

        assert result_table_grid.dashGridOptions.get("rowSelection") == expected_row_selection

    def test_call_default_dash_grid_options_for_custom_ag_grid(self):
        @capture("ag_grid")
        def custom_dash_ag_grid(data_frame):
            return dag.AgGrid(
                # Keep configuration concise: Table model code must not depend on assumed config input.
                columnDefs=[{"field": col} for col in data_frame.columns],
                rowData=data_frame.to_dict("records"),
            )

        table = vm.Table(figure=custom_dash_ag_grid(data_frame=px.data.gapminder()))
        table.pre_build()

        # table() is the same as table.__call__()
        result_table = table()

        # Extract dag.AgGrid
        result_table_grid = result_table.children[0]

        assert result_table_grid.dashGridOptions.get("theme") == {"function": "vizroTheme(themeQuartz, agGrid)"}

    def test_call_suppress_cell_focus_no_actions(self, standard_ag_grid):
        # No actions - cell focus and row hover highlighting are suppressed.
        table = vm.Table(figure=standard_ag_grid)
        table.pre_build()
        result_table_grid = table().children[0]

        assert result_table_grid.dashGridOptions.get("suppressCellFocus") is True
        assert result_table_grid.dashGridOptions.get("suppressRowHoverHighlight") is True

    def test_call_suppress_cell_focus_row_selection_actions(self):
        # All actions are row-selection (value not a cell-click field) - cell focus is suppressed but hover is not.
        table = vm.Table(
            figure=dash_ag_grid(data_frame=px.data.gapminder()),
            actions=va.set_controls(controls=["control_id"], value="continent"),
        )
        table.pre_build()
        result_table_grid = table().children[0]

        assert result_table_grid.dashGridOptions.get("suppressCellFocus") is True
        assert result_table_grid.dashGridOptions.get("suppressRowHoverHighlight") is None

    def test_call_no_suppress_cell_focus_cell_click_actions(self):
        # All actions are cell-click actions (value is a cell-click field) - cell focus is NOT suppressed.
        table = vm.Table(
            figure=dash_ag_grid(data_frame=px.data.gapminder()),
            actions=va.set_controls(controls=["control_id"], value="column"),
        )
        table.pre_build()
        result_table_grid = table().children[0]

        assert result_table_grid.dashGridOptions.get("suppressCellFocus") is None


class TestTableAgGridPreBuild:
    def test_pre_build_no_underlying_id(self, standard_ag_grid):
        table = vm.Table(id="text_ag_grid", figure=standard_ag_grid)
        table.pre_build()

        assert table._inner_component_id == "__input_text_ag_grid"

    def test_pre_build_underlying_id(self, ag_grid_with_id):
        table = vm.Table(id="text_ag_grid", figure=ag_grid_with_id)
        table.pre_build()

        assert table._inner_component_id == "underlying_ag_grid_id"

    def test_pre_build_duplicate_input_id(self):
        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Test Page",
                    components=[
                        vm.Table(figure=dash_ag_grid(id="duplicate_ag_grid_id", data_frame=px.data.gapminder())),
                        vm.Table(figure=dash_ag_grid(id="duplicate_ag_grid_id", data_frame=px.data.gapminder())),
                    ],
                )
            ]
        )
        with pytest.raises(
            DuplicateIDError,
            match="CapturedCallable with id=duplicate_ag_grid_id has an id that is",
        ):
            Vizro().build(dashboard)

    def test_pre_build_duplicate_input_id_and_button_id(self):
        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Test Page",
                    components=[
                        vm.Table(figure=dash_ag_grid(id="duplicate_ag_grid_id", data_frame=px.data.gapminder())),
                        vm.Button(id="duplicate_ag_grid_id"),
                    ],
                )
            ]
        )
        with pytest.raises(
            DuplicateIDError,
            match="CapturedCallable with id=duplicate_ag_grid_id has an id that is",
        ):
            Vizro().build(dashboard)


class TestTableAgGridBuild:
    def test_ag_grid_build_mandatory_only(self, standard_ag_grid):
        table = vm.Table(figure=standard_ag_grid)
        table.pre_build()
        result_table = table.build()
        expected_table = dcc.Loading(
            html.Div(
                [
                    dcc.Store(id=f"{table.id}_action_trigger"),
                    None,
                    None,
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(result_table, expected_table, keys_to_strip={"id"})

    @pytest.mark.parametrize(
        "table, underlying_id_expected",
        [
            ("ag_grid_with_id", "underlying_ag_grid_id"),
            ("standard_ag_grid", "__input_text_ag_grid"),
        ],
    )
    def test_ag_grid_build_with_and_without_underlying_id(self, table, underlying_id_expected, request):
        table = vm.Table(id="text_ag_grid", figure=request.getfixturevalue(table))
        table.pre_build()
        result_table = table.build()

        expected_table = dcc.Loading(
            html.Div(
                [
                    dcc.Store(id="text_ag_grid_action_trigger"),
                    None,
                    None,
                    html.Div(
                        id="text_ag_grid",
                        children=[html.Div(id=underlying_id_expected)],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(result_table, expected_table)

    def test_ag_grid_build_title_header_footer(self, standard_ag_grid):
        table = vm.Table(
            figure=standard_ag_grid, title="Title", header="""#### Subtitle""", footer="""SOURCE: **DATA**"""
        )
        table.pre_build()
        result_table = table.build()

        expected_table = dcc.Loading(
            html.Div(
                children=[
                    dcc.Store(id=f"{table.id}_action_trigger"),
                    html.H3([html.Span("Title"), None], className="figure-title"),
                    vdc.Markdown("""#### Subtitle""", className="figure-header"),
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    vdc.Markdown("""SOURCE: **DATA**""", className="figure-footer"),
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(result_table, expected_table, keys_to_strip={"id"})

    def test_ag_grid_build_with_description(self, standard_ag_grid):
        table = vm.Table(
            figure=standard_ag_grid,
            title="Title",
            description=vm.Tooltip(text="Tooltip test", icon="Info", id="info"),
        )
        table.pre_build()
        result_table = table.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=vdc.Markdown("Tooltip test", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]
        expected_table = dcc.Loading(
            html.Div(
                children=[
                    dcc.Store(id=f"{table.id}_action_trigger"),
                    html.H3([html.Span("Title"), *expected_description], className="figure-title"),
                    None,
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    None,
                ],
                className="figure-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(result_table, expected_table, keys_to_strip={"id"})
