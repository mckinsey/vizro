"""Unit tests for vizro.models.Table."""

import re

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.managers._model_manager import DuplicateIDError
from vizro.models._action._action import Action
from vizro.tables import dash_data_table


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
        assert table._action_outputs == {
            "__default__": f"{table.id}.children",
            "figure": f"{table.id}.children",
        }

    def test_create_table_mandatory_and_optional(self, dash_data_table_with_id):
        table = vm.Table(
            id="table-id",
            figure=dash_data_table_with_id,
            title="Title",
            description="Test description",
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
        assert table._action_outputs == {
            "__default__": f"{table.id}.children",
            "figure": f"{table.id}.children",
            "title": f"{table.id}_title.children",
            "header": f"{table.id}_header.children",
            "footer": f"{table.id}_footer.children",
            "description": f"{table.description.id}-text.children",
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
                "defined with decorator @capture('table')."
            ),
        ):
            vm.Table(figure=standard_go_chart)

    def test_captured_callable_wrong_mode(self, standard_ag_grid):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "CapturedCallable was defined with @capture('ag_grid') rather than @capture('table') and so "
                "is not compatible with the model."
            ),
        ):
            vm.Table(figure=standard_ag_grid)

    def test_is_model_inheritable(self, standard_dash_table):
        class MyTable(vm.Table):
            pass

        my_table = MyTable(figure=standard_dash_table)

        assert hasattr(my_table, "id")
        assert my_table.type == "table"
        assert my_table.figure == standard_dash_table
        assert my_table.actions == []

    def test_set_action_via_validator(self, standard_dash_table, identity_action_function):
        table = vm.Table(figure=standard_dash_table, actions=[Action(function=identity_action_function())])
        actions_chain = table.actions[0]
        assert actions_chain.trigger.component_property == "active_cell"


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
        assert table().id == "__input_table"

    def test_underlying_id_is_provided(self, dash_data_table_with_id):
        table = vm.Table(figure=dash_data_table_with_id)
        table.pre_build()
        # table() is the same as table.__call__()
        assert table().id == "underlying_table_id"


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

    def test_pre_build_underlying_table_id(self, dash_data_table_with_id, filter_interaction_action):
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
                    dcc.Markdown("""#### Subtitle""", className="figure-header"),
                    html.Div(
                        children=[html.Div()],
                        className="table-container",
                    ),
                    dcc.Markdown("""SOURCE: **DATA**""", className="figure-footer"),
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
            description=vm.Tooltip(text="Tooltip test", icon="info", id="info"),
        )
        table.pre_build()
        table = table.build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", className="card-text"),
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
