"""Unit tests for vizro.models.AgGrid."""

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
from vizro.tables import dash_ag_grid


@pytest.fixture
def dash_ag_grid_with_arguments():
    return dash_ag_grid(data_frame=px.data.gapminder(), defaultColDef={"resizable": False, "sortable": False})


@pytest.fixture
def dash_ag_grid_with_str_dataframe():
    return dash_ag_grid(data_frame="gapminder")


class TestAgGridInstantiation:
    def test_create_graph_mandatory_only(self, standard_ag_grid):
        ag_grid = vm.AgGrid(figure=standard_ag_grid)

        assert hasattr(ag_grid, "id")
        assert ag_grid.type == "ag_grid"
        assert ag_grid.figure == standard_ag_grid
        assert ag_grid.actions == []

    @pytest.mark.parametrize("id", ["id_1", "id_2"])
    def test_create_ag_grid_mandatory_and_optional(self, standard_ag_grid, id):
        ag_grid = vm.AgGrid(figure=standard_ag_grid, id=id, actions=[])

        assert ag_grid.id == id
        assert ag_grid.type == "ag_grid"
        assert ag_grid.figure == standard_ag_grid

    def test_mandatory_figure_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.AgGrid()

    def test_wrong_captured_callable(self, standard_dash_table):
        with pytest.raises(ValidationError, match="CapturedCallable mode mismatch"):
            vm.AgGrid(figure=standard_dash_table)

    def test_failed_ag_grid_with_no_captured_callable(self, standard_go_chart):
        with pytest.raises(ValidationError, match="must provide a valid CapturedCallable object"):
            vm.AgGrid(figure=standard_go_chart)

    def test_failed_ag_grid_with_wrong_captured_callable(self, standard_px_chart):
        with pytest.raises(ValidationError, match="CapturedCallable mode mismatch. Expected ag_grid but got graph."):
            vm.AgGrid(figure=standard_px_chart)

    def test_set_action_via_validator(self, standard_ag_grid, identity_action_function):
        ag_grid = vm.AgGrid(figure=standard_ag_grid, actions=[Action(function=identity_action_function())])
        actions_chain = ag_grid.actions[0]
        assert actions_chain.trigger.component_property == "cellClicked"


class TestDunderMethodsAgGrid:
    def test_getitem_known_args(self, dash_ag_grid_with_arguments):
        ag_grid = vm.AgGrid(figure=dash_ag_grid_with_arguments)
        assert ag_grid["defaultColDef"] == {"resizable": False, "sortable": False}
        assert ag_grid["type"] == "ag_grid"

    def test_getitem_unknown_args(self, standard_ag_grid):
        ag_grid = vm.AgGrid(figure=standard_ag_grid)
        with pytest.raises(KeyError):
            ag_grid["unknown_args"]


class TestAttributesAgGrid:
    # Testing at this low implementation level as mocking callback contexts skips checking for creation of these objects
    def test_ag_grid_filter_interaction_attributes(self, ag_grid_with_id):
        ag_grid = vm.AgGrid(figure=ag_grid_with_id, title="Gapminder", actions=[])
        ag_grid.pre_build()
        assert hasattr(ag_grid, "_filter_interaction_input")
        assert "modelID" in ag_grid._filter_interaction_input


class TestProcessAgGridDataFrame:
    def test_process_figure_data_frame_str_df(self, dash_ag_grid_with_str_dataframe, gapminder):
        data_manager["gapminder"] = gapminder
        ag_grid = vm.AgGrid(id="ag_grid", figure=dash_ag_grid_with_str_dataframe)
        assert data_manager[ag_grid["data_frame"]].load().equals(gapminder)

    def test_process_figure_data_frame_df(self, standard_ag_grid, gapminder):
        ag_grid = vm.AgGrid(id="ag_grid", figure=standard_ag_grid)
        assert data_manager[ag_grid["data_frame"]].load().equals(gapminder)


class TestPreBuildAgGrid:
    def test_pre_build_no_actions_no_underlying_ag_grid_id(self, standard_ag_grid):
        ag_grid = vm.AgGrid(id="text_ag_grid", figure=standard_ag_grid)
        ag_grid.pre_build()

        assert ag_grid._input_component_id == "__input_text_ag_grid"

    def test_pre_build_actions_underlying_ag_grid_id(self, ag_grid_with_id, filter_interaction_action):
        ag_grid = vm.AgGrid(id="text_ag_grid", figure=ag_grid_with_id, actions=[filter_interaction_action])
        ag_grid.pre_build()
        assert ag_grid._input_component_id == "underlying_ag_grid_id"


class TestBuildAgGrid:
    def test_ag_grid_build_mandatory_only(self, standard_ag_grid, gapminder):
        ag_grid = vm.AgGrid(id="text_ag_grid", figure=standard_ag_grid)
        ag_grid.pre_build()
        ag_grid = ag_grid.build()
        expected_ag_grid = dcc.Loading(
            [
                None,
                html.Div(
                    id="text_ag_grid",
                    children=dash_ag_grid(data_frame=gapminder, id="__input_text_ag_grid")(),
                    className="table-container",
                ),
            ],
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(ag_grid, expected_ag_grid)

    def test_ag_grid_build_with_underlying_id(self, ag_grid_with_id_and_conf, filter_interaction_action, gapminder):
        ag_grid = vm.AgGrid(id="text_ag_grid", figure=ag_grid_with_id_and_conf, actions=[filter_interaction_action])
        ag_grid.pre_build()
        ag_grid = ag_grid.build()

        expected_ag_grid = dcc.Loading(
            [
                None,
                html.Div(
                    id="text_ag_grid",
                    children=dash_ag_grid(data_frame=gapminder, id="underlying_ag_grid_id")(),
                    className="table-container",
                ),
            ],
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )

        assert_component_equal(ag_grid, expected_ag_grid)
