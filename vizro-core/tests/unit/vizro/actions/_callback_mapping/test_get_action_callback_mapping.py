"""Unit tests for vizro.actions._callback_mapping._get_action_callback_mapping file."""

import dash
import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.actions._callback_mapping._get_action_callback_mapping import _get_action_callback_mapping
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
def managers_one_page_four_controls_two_graphs_filter_interaction():
    """Instantiates managers with one page that contains four controls, two graphs and filter interaction."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(
                id="scatter_chart",
                figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                actions=[
                    vm.Action(id="filter_interaction_action", function=filter_interaction(targets=["scatter_chart_2"]))
                ],
            ),
            vm.Graph(
                id="scatter_chart_2",
                figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                actions=[vm.Action(id="custom_action", function=custom_action_example())],
            ),
            vm.Button(
                id="export_data_button",
                actions=[
                    vm.Action(id="export_data_action", function=export_data()),
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
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def export_data_inputs_expected():
    return {
        "filters": [
            dash.State("filter_continent_selector", "value"),
            dash.State("filter_country_selector", "value"),
        ],
        "parameters": [],
        "filter_interaction": [
            dash.State("scatter_chart", "clickData"),
        ],
        "theme_selector": [],
    }


@pytest.fixture
def action_callback_inputs_expected():
    return {
        "filters": [
            dash.State("filter_continent_selector", "value"),
            dash.State("filter_country_selector", "value"),
        ],
        "parameters": [
            dash.State("parameter_x_selector", "value"),
            dash.State("parameter_y_selector", "value"),
        ],
        "filter_interaction": [
            dash.State("scatter_chart", "clickData"),
        ],
        "theme_selector": dash.State("theme_selector", "on"),
    }


@pytest.fixture
def action_callback_outputs_expected(request):
    return {
        f'{target.split(".")[0]}': dash.Output(target.split(".")[0], target.split(".")[1]) for target in request.param
    }


@pytest.fixture
def export_data_outputs_expected(request):
    return {
        f"download-dataframe_{target}": dash.Output(
            {"action_id": "export_data_action", "target_id": target, "type": "download-dataframe"}, "data"
        )
        for target in request.param
    }


@pytest.fixture
def export_data_components_expected(request):
    return [
        dash.dcc.Download(id={"type": "download-dataframe", "action_id": "export_data_action", "target_id": target})
        for target in request.param
    ]


@pytest.fixture
def export_data_action_targets(request):
    return request.param


@pytest.mark.usefixtures("managers_one_page_four_controls_two_graphs_filter_interaction")
class TestCallbackMapping:
    """Tests action callback mapping for predefined actions."""

    @pytest.mark.parametrize(
        "action_id, expected_inputs",
        [
            ("filter_action_filter_continent", "action_callback_inputs_expected"),
            ("filter_interaction_action", "action_callback_inputs_expected"),
            ("parameter_action_parameter_x", "action_callback_inputs_expected"),
            ("on_page_load_action_action_test_page", "action_callback_inputs_expected"),
            ("export_data_action", "export_data_inputs_expected"),
        ],
    )
    def test_action_callback_mapping_inputs(self, action_id, expected_inputs, request):
        result = _get_action_callback_mapping(
            action_id=action_id,
            argument="inputs",
        )

        expected_inputs = request.getfixturevalue(expected_inputs)
        assert result == expected_inputs

    @pytest.mark.parametrize(
        "action_id, action_callback_outputs_expected",
        [
            ("filter_action_filter_continent", ["scatter_chart.figure", "scatter_chart_2.figure"]),
            ("filter_interaction_action", ["scatter_chart_2.figure"]),
            ("parameter_action_parameter_x", ["scatter_chart.figure", "scatter_chart_2.figure"]),
            ("on_page_load_action_action_test_page", ["scatter_chart.figure", "scatter_chart_2.figure"]),
        ],
        indirect=["action_callback_outputs_expected"],
    )
    def test_action_callback_mapping_outputs(self, action_id, action_callback_outputs_expected):
        result = _get_action_callback_mapping(
            action_id=action_id,
            argument="outputs",
        )
        assert result == action_callback_outputs_expected

    @pytest.mark.parametrize(
        "export_data_action_targets, export_data_outputs_expected",
        [
            (None, ["scatter_chart", "scatter_chart_2"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_mapping_outputs(self, export_data_action_targets, export_data_outputs_expected):
        export_data_action = model_manager["export_data_action"]
        export_data_action.function = (
            export_data(targets=export_data_action_targets) if export_data_action_targets else export_data()
        )

        result = _get_action_callback_mapping(
            action_id="export_data_action",
            argument="outputs",
        )

        assert result == export_data_outputs_expected

    @pytest.mark.parametrize(
        "export_data_action_targets, export_data_components_expected",
        [
            (None, ["scatter_chart", "scatter_chart_2"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_mapping_components(self, export_data_action_targets, export_data_components_expected):
        export_data_action = model_manager["export_data_action"]
        export_data_action.function = (
            export_data(targets=export_data_action_targets) if export_data_action_targets else export_data()
        )

        result = _get_action_callback_mapping(
            action_id="export_data_action",
            argument="components",
        )
        assert repr(result) == repr(export_data_components_expected)

    def test_known_action_unknown_argument(self):
        result = _get_action_callback_mapping(
            action_id="export_data_action",
            argument="unknown-argument",
        )
        assert result == {}

    @pytest.mark.parametrize(
        "argument, expected",
        [
            ("inputs", {}),
            ("outputs", {}),
            pytest.param("components", [], marks=pytest.mark.xfail()),
            ("unknown-argument", {}),
        ],
    )
    def test_custom_action_mapping(self, argument, expected):
        result = _get_action_callback_mapping(
            action_id="custom_action",
            argument=argument,
        )
        assert result == expected

    @pytest.mark.parametrize(
        "argument, expected",
        [
            ("inputs", {}),
            ("outputs", {}),
            pytest.param("components", [], marks=pytest.mark.xfail()),
            ("unknown-argument", {}),
        ],
    )
    def test_custom_action_with_known_name_mapping(self, argument, expected):
        result = _get_action_callback_mapping(
            action_id="export_data_custom_action",
            argument=argument,
        )
        assert result == expected
