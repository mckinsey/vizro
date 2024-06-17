"""Unit tests for vizro.models.Table."""

import pytest
from asserts import assert_component_equal
from dash import dcc, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from vizro.managers import data_manager
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

    @pytest.mark.parametrize("id", ["id_1", "id_2"])
    def test_create_table_mandatory_and_optional(self, standard_dash_table, id):
        table = vm.Table(id=id, figure=standard_dash_table, actions=[])

        assert table.id == id
        assert table.type == "table"
        assert table.figure == standard_dash_table

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Table()

    def test_wrong_captured_callable(self, standard_ag_grid):
        with pytest.raises(ValidationError, match="CapturedCallable mode mismatch"):
            vm.Table(figure=standard_ag_grid)

    def test_failed_table_with_no_captured_callable(self, standard_go_chart):
        with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
            vm.Table(figure=standard_go_chart)

    def test_failed_table_with_wrong_captured_callable(self, standard_px_chart):
        with pytest.raises(ValidationError, match="CapturedCallable mode mismatch. Expected table but got graph."):
            vm.Table(figure=standard_px_chart)

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


class TestAttributesTable:
    def test_table_filter_interaction_attributes(self, dash_data_table_with_id):
        table = vm.Table(figure=dash_data_table_with_id, title="Gapminder", actions=[])
        table.pre_build()
        assert hasattr(table, "_filter_interaction_input")
        assert "modelID" in table._filter_interaction_input


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
    def test_pre_build_no_actions_no_underlying_table_id(self, standard_dash_table):
        table = vm.Table(id="text_table", figure=standard_dash_table)
        table.pre_build()

        assert table._input_component_id == "__input_text_table"

    def test_pre_build_actions_underlying_table_id(self, dash_data_table_with_id, filter_interaction_action):
        table = vm.Table(id="text_table", figure=dash_data_table_with_id, actions=[filter_interaction_action])
        table.pre_build()

        assert table._input_component_id == "underlying_table_id"


class TestBuildTable:
    def test_table_build_mandatory_only(self, standard_dash_table, gapminder):
        table = vm.Table(id="text_table", figure=standard_dash_table)
        table.pre_build()
        table = table.build()
        expected_table = dcc.Loading(
            html.Div(
                [
                    None,
                    html.Div(dash_data_table(id="__input_text_table", data_frame=gapminder)(), id="text_table"),
                ],
                className="table-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table)

    def test_table_build_with_underlying_id(self, dash_data_table_with_id, filter_interaction_action, gapminder):
        table = vm.Table(id="text_table", figure=dash_data_table_with_id, actions=[filter_interaction_action])
        table.pre_build()
        table = table.build()

        expected_table = dcc.Loading(
            html.Div(
                [
                    None,
                    html.Div(dash_data_table(id="underlying_table_id", data_frame=gapminder)(), id="text_table"),
                ],
                className="table-container",
            ),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(table, expected_table)
