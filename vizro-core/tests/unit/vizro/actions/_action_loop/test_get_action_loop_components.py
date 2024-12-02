"""Unit tests for vizro.actions._action_loop._get_action_loop_components file."""

import pytest
from asserts import STRIP_ALL, assert_component_equal
from dash import dcc, html
from dash._utils import stringify_id

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.actions._action_loop._get_action_loop_components import _get_action_loop_components
from vizro.managers import model_manager


@pytest.fixture
def fundamental_components():
    return [
        dcc.Store(id="action_finished"),
        dcc.Store(id="remaining_actions", data=[]),
        html.Div(id="cycle_breaker_div", hidden=True),
        dcc.Store(id="cycle_breaker_empty_output_store"),
    ]


@pytest.fixture
def gateway_components(request):
    components = request.param
    actions_chain_ids = [model_manager[component].actions[0].id for component in components]
    return [
        dcc.Store(id={"type": "gateway_input", "trigger_id": actions_chain_id}, data=actions_chain_id)
        for actions_chain_id in actions_chain_ids
    ]


@pytest.fixture
def action_trigger_components(request):
    components = request.param
    actions_ids = [model_manager[component].actions[0].actions[0].id for component in components]
    return [dcc.Store(id={"type": "action_trigger", "action_name": action_id}) for action_id in actions_ids]


@pytest.fixture
def action_trigger_actions_id_component(request):
    components = request.param
    actions_ids = [model_manager[component].actions[0].actions[0].id for component in components]
    return dcc.Store(id="action_trigger_actions_id", data=actions_ids)


@pytest.fixture
def trigger_to_actions_chain_mapper_component(request):
    components = request.param
    actions_chain_ids = [model_manager[component].actions[0].id for component in components]
    return dcc.Store(
        id="trigger_to_actions_chain_mapper",
        data={
            actions_chain_id: [action.id for action in model_manager[actions_chain_id].actions]
            for actions_chain_id in actions_chain_ids
        },
    )


@pytest.fixture
def managers_one_page_two_components_two_controls(vizro_app, dash_data_table_with_id):
    """Instantiates managers with one page that contains two controls and two components."""
    vm.Dashboard(
        pages=[
            vm.Page(
                id="test_page",
                title="First page",
                components=[
                    vm.Table(
                        id="vizro_table",
                        figure=dash_data_table_with_id,
                        actions=[
                            vm.Action(
                                id="table_filter_interaction_action",
                                function=filter_interaction(targets=["scatter_chart"]),
                            )
                        ],
                    ),
                    vm.Graph(id="scatter_chart", figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap")),
                    vm.Button(
                        id="export_data_button", actions=[vm.Action(id="export_data_action", function=export_data())]
                    ),
                ],
                controls=[
                    vm.Filter(
                        id="filter_continent", column="continent", selector=vm.Dropdown(id="filter_continent_selector")
                    ),
                    vm.Parameter(
                        id="parameter_x",
                        targets=["scatter_chart.x"],
                        selector=vm.Dropdown(id="parameter_x_selector", options=["lifeExp", "gdpPercap", "pop"]),
                    ),
                ],
            )
        ]
    )

    Vizro._pre_build()


@pytest.fixture
def managers_one_page_no_actions(vizro_app):
    """Instantiates managers with one "empty" page."""
    vm.Dashboard(
        pages=[
            vm.Page(
                id="test_page_no_actions",
                title="Second page",
                components=[
                    vm.Card(text=""),
                ],
            ),
        ]
    )

    Vizro._pre_build()


class TestGetActionLoopComponents:
    """Tests getting required components for the action loop."""

    @pytest.mark.usefixtures("managers_one_page_no_actions")
    def test_no_components(self):
        result = _get_action_loop_components()
        assert_component_equal(result, html.Div(id="action_loop_components_div"))

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    @pytest.mark.parametrize(
        "gateway_components, "
        "action_trigger_components, "
        "action_trigger_actions_id_component, "
        "trigger_to_actions_chain_mapper_component",
        [
            (
                ["test_page", "vizro_table", "export_data_button", "filter_continent_selector", "parameter_x_selector"],
                ["test_page", "vizro_table", "export_data_button", "filter_continent_selector", "parameter_x_selector"],
                ["test_page", "vizro_table", "export_data_button", "filter_continent_selector", "parameter_x_selector"],
                ["test_page", "vizro_table", "export_data_button", "filter_continent_selector", "parameter_x_selector"],
            )
        ],
        indirect=True,
    )
    def test_all_action_loop_components(
        self,
        fundamental_components,
        gateway_components,
        action_trigger_components,
        action_trigger_actions_id_component,
        trigger_to_actions_chain_mapper_component,
    ):
        result = _get_action_loop_components()
        expected = html.Div(
            id="action_loop_components_div",
            children=[
                *fundamental_components,
                *gateway_components,
                *action_trigger_components,
                action_trigger_actions_id_component,
                trigger_to_actions_chain_mapper_component,
            ],
        )

        # Data in these dcc.Stores is arbitrarily order. Sort in advance to ensure that assert_component_equal
        # is order-agnostic for their data.
        for key in ("action_trigger_actions_id", "trigger_to_actions_chain_mapper"):
            result[key].data = sorted(result[key].data)
            expected[key].data = sorted(expected[key].data)

        # Validate the action_loop_components_div wrapper.
        assert_component_equal(result, expected, keys_to_strip=STRIP_ALL)

        # Order of dcc.Stores inside div wrapper is arbitrary so sort by stringified id to do order-agnostic comparison.
        assert_component_equal(
            sorted(result.children, key=lambda component: stringify_id(component.id)),
            sorted(expected.children, key=lambda component: stringify_id(component.id)),
        )
