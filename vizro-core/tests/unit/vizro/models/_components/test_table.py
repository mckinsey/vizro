"""Unit tests for vizro.models.Table."""

import re
import warnings

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pytest
import vizro_dash_components as vdc
from asserts import STRIP_ALL, assert_component_equal
from dash import dcc, html, no_update

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.managers._model_manager import DuplicateIDError
from vizro.models._action._action import Action
from vizro.models._components.table import DAG_AG_GRID_PROPERTIES
from vizro.models.types import capture
from vizro.tables import dash_ag_grid


class TestTableAgGrid:
    """`vm.Table` with a `dash_ag_grid` figure — the recommended, warning-free table."""

    def test_ag_grid_figure_is_warning_free(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", FutureWarning)
            vm.Table(figure=dash_ag_grid(data_frame=px.data.gapminder()))

    def test_ag_grid_action_triggers(self):
        table = vm.Table(id="ag_table", figure=dash_ag_grid(data_frame=px.data.gapminder()))
        assert table._action_triggers == {"__default__": "ag_table_action_trigger.data"}

    def test_ag_grid_exposes_inner_properties_as_action_io(self):
        table = vm.Table(id="ag_table", figure=dash_ag_grid(data_frame=px.data.gapminder()))
        assert "cellClicked" in table._action_inputs
        assert "cellClicked" in table._action_outputs


# ==============================================================================================================
# AG-Grid coverage for `vm.Table(figure=dash_ag_grid(...))` — the canonical `Table` backing.
#
# These classes mirror the behavioral coverage that historically lived in test_legacy_ag_grid.py (against the removed
# `AgGrid` model). AG-Grid figures emit no deprecation warning, so these tests run warning-free.
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
