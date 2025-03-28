"""Unit tests for vizro actions callback inputs/outputs/_dash_components mapping."""

import dash
import pytest
from asserts import assert_component_equal

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import model_manager
from vizro.models.types import capture


@capture("action")
def custom_action_example():
    pass


# custom action with same name as some predefined action
def get_custom_action_with_known_name():
    @capture("action")
    def export_data():
        pass

    return export_data()


@pytest.fixture
def config_for_testing_all_components_with_actions(request, dash_data_table_with_id):
    """Instantiates managers with one page that contains four controls, two graphs and filter interaction."""
    # If the fixture is parametrised set the targets. Otherwise, set export_data without targets.
    export_data_action_function = (
        export_data(id="export_data_action", targets=request.param)
        if hasattr(request, "param")
        else export_data(id="export_data_action")
    )
    tab_1 = vm.Container(
        title="test_container_1",
        components=[
            vm.Graph(
                id="scatter_chart",
                figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                actions=[
                    vm.Action(function=filter_interaction(id="filter_interaction_action", targets=["scatter_chart_2"]))
                ],
            ),
            vm.Container(
                title="test_nested_container_1",
                components=[
                    vm.Graph(
                        id="scatter_chart_2",
                        figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                        actions=[vm.Action(id="custom_action", function=custom_action_example())],
                    ),
                ],
            ),
        ],
    )

    tab_2 = vm.Container(
        title="test_container_2",
        components=[
            vm.Table(
                id="vizro_table",
                figure=dash_data_table_with_id,
                actions=[
                    vm.Action(
                        function=filter_interaction(
                            id="table_filter_interaction_action", targets=["scatter_chart", "scatter_chart_2"]
                        ),
                    )
                ],
            ),
        ],
    )

    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Tabs(tabs=[tab_1, tab_2]),
            vm.Button(
                id="export_data_button",
                actions=[
                    vm.Action(function=export_data_action_function),
                    vm.Action(id="export_data_custom_action", function=get_custom_action_with_known_name()),
                ],
            ),
        ],
        controls=[
            vm.Filter(id="filter_continent", column="continent", selector=vm.Dropdown(id="filter_continent_selector")),
            vm.Filter(id="filter_country", column="country", selector=vm.Dropdown(id="filter_country_selector")),
            vm.Parameter(
                id="parameter_x",
                targets=["scatter_chart.x", "scatter_chart_2.x"],
                selector=vm.Dropdown(
                    id="parameter_x_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                    multi=False,
                    value="gdpPercap",
                ),
            ),
            vm.Parameter(
                id="parameter_y",
                targets=["scatter_chart.y", "scatter_chart_2.y"],
                selector=vm.Dropdown(
                    id="parameter_y_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                    multi=False,
                    value="lifeExp",
                ),
            ),
            vm.Parameter(
                id="vizro_table_row_selectable",
                targets=["vizro_table.row_selectable"],
                selector=vm.Dropdown(
                    id="parameter_table_row_selectable",
                    options=["multi", "single"],
                    multi=False,
                    value="single",
                ),
            ),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def action_callback_inputs_expected():
    return {
        "_controls": {
            "filters": [
                dash.State("filter_continent_selector", "value"),
                dash.State("filter_country_selector", "value"),
            ],
            "parameters": [
                dash.State("parameter_x_selector", "value"),
                dash.State("parameter_y_selector", "value"),
                dash.State("parameter_table_row_selectable", "value"),
            ],
            "filter_interaction": [
                {"clickData": dash.State("scatter_chart", "clickData"), "modelID": dash.State("scatter_chart", "id")},
                {
                    "active_cell": dash.State("underlying_table_id", "active_cell"),
                    "derived_viewport_data": dash.State("underlying_table_id", "derived_viewport_data"),
                    "modelID": dash.State("vizro_table", "id"),
                },
            ],
        }
    }


@pytest.fixture
def action_callback_outputs_expected(request):
    targets = request.param
    return {
        target["component_id"]: dash.Output(target["component_id"], target["component_property"]) for target in targets
    }


@pytest.fixture
def export_data_outputs_expected(request):
    return {
        f"download_dataframe_{target}": dash.Output(
            {"action_id": "export_data_action", "target_id": target, "type": "download_dataframe"}, "data"
        )
        for target in request.param
    }


@pytest.fixture
def export_data_components_expected(request):
    return [
        dash.dcc.Download(id={"type": "download_dataframe", "action_id": "export_data_action", "target_id": target})
        for target in request.param
    ]


@pytest.mark.usefixtures("config_for_testing_all_components_with_actions")
class TestCallbackMapping:
    """Tests action callback mapping for predefined and custom actions."""

    @pytest.mark.parametrize(
        "action_id",
        [
            "__filter_action_filter_continent",
            "filter_interaction_action",
            "__parameter_action_parameter_x",
            "__on_page_load_action_action_test_page",
            "export_data_action",
        ],
    )
    def test_action_callback_mapping_inputs(self, action_id, action_callback_inputs_expected):
        result = model_manager[action_id]._transformed_inputs
        assert result == action_callback_inputs_expected

    @pytest.mark.parametrize(
        "action_id, action_callback_outputs_expected",
        [
            (
                "__filter_action_filter_continent",
                [
                    {"component_id": "scatter_chart", "component_property": "figure"},
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                    {"component_id": "vizro_table", "component_property": "children"},
                ],
            ),
            (
                "filter_interaction_action",
                [
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                ],
            ),
            (
                "table_filter_interaction_action",
                [
                    {"component_id": "scatter_chart", "component_property": "figure"},
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                ],
            ),
            (
                "__parameter_action_parameter_x",
                [
                    {"component_id": "scatter_chart", "component_property": "figure"},
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                ],
            ),
            (
                "__parameter_action_parameter_y",
                [
                    {"component_id": "scatter_chart", "component_property": "figure"},
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                ],
            ),
            (
                "__on_page_load_action_action_test_page",
                [
                    {"component_id": "scatter_chart", "component_property": "figure"},
                    {"component_id": "scatter_chart_2", "component_property": "figure"},
                    {"component_id": "vizro_table", "component_property": "children"},
                ],
            ),
            (
                "__parameter_action_vizro_table_row_selectable",
                [{"component_id": "vizro_table", "component_property": "children"}],
            ),
        ],
        indirect=["action_callback_outputs_expected"],
    )
    def test_action_callback_mapping_outputs(self, action_id, action_callback_outputs_expected):
        result = model_manager[action_id]._transformed_outputs
        assert result == action_callback_outputs_expected

    @pytest.mark.parametrize(
        "export_data_outputs_expected", [("scatter_chart", "scatter_chart_2", "vizro_table")], indirect=True
    )
    def test_export_data_no_targets_set_mapping_outputs(self, export_data_outputs_expected):
        result = model_manager["export_data_action"]._transformed_outputs

        assert result == export_data_outputs_expected

    @pytest.mark.parametrize(
        "config_for_testing_all_components_with_actions, export_data_outputs_expected",
        [
            ([], ["scatter_chart", "scatter_chart_2", "vizro_table"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_targets_set_mapping_outputs(
        self, config_for_testing_all_components_with_actions, export_data_outputs_expected
    ):
        result = model_manager["export_data_action"]._transformed_outputs
        assert result == export_data_outputs_expected

    @pytest.mark.parametrize(
        "export_data_components_expected", [("scatter_chart", "scatter_chart_2", "vizro_table")], indirect=True
    )
    def test_export_data_no_targets_set_mapping_components(self, export_data_components_expected):
        result_components = model_manager["export_data_action"]._dash_components
        assert_component_equal(result_components, export_data_components_expected)

    @pytest.mark.parametrize(
        "config_for_testing_all_components_with_actions, export_data_components_expected",
        [
            ([], ["scatter_chart", "scatter_chart_2", "vizro_table"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_targets_set_mapping_components(
        self, config_for_testing_all_components_with_actions, export_data_components_expected
    ):
        result_components = model_manager["export_data_action"]._dash_components
        assert_component_equal(result_components, export_data_components_expected)

    # "export_data_custom_action" represents a unique scenario within custom actions, where the function's name
    # coincides with an already predefined action function (in this instance, "export_data").
    # It requires handling them as conventional custom actions.
    @pytest.mark.parametrize("action_id", ["custom_action", "export_data_custom_action"])
    def test_custom_action_mapping(self, action_id):
        result = model_manager[action_id]

        assert result.inputs == []
        assert result.outputs == []
        assert result._dash_components == []
