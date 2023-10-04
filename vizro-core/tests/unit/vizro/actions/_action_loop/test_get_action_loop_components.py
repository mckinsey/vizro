"""Unit tests for vizro.actions._action_loop._get_action_loop_components file."""

import dash
import pytest
from dash import dcc, html

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.actions._action_loop._get_action_loop_components import _get_action_loop_components
from vizro.managers import model_manager


@pytest.fixture
def fundamental_components():
    return [
        dcc.Store(id="action_finished"),
        dcc.Store(id="remaining_actions", data=[]),
        html.Div(id="cycle_breaker_div", style={"display": "hidden"}),
        dcc.Store(id="cycle_breaker_empty_output_store"),
    ]


@pytest.fixture
def gateway_components(request):
    components = request.param
    actions_chain_ids = [model_manager[component].actions[0].id for component in components]
    return [
        dcc.Store(
            id={"type": "gateway_input", "trigger_id": actions_chain_id},
            data=f"{actions_chain_id}",
        )
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
    return dcc.Store(
        id="action_trigger_actions_id",
        data=list(actions_ids),
    )


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
def managers_one_page_two_components_two_controls():
    """Instantiates managers with one page that contains two controls and two components."""
    page = vm.Page(
        id="test_page",
        title="First page",
        components=[
            vm.Graph(
                id="scatter_chart",
                figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap"),
            ),
            vm.Button(
                id="export_data_button",
                actions=[vm.Action(id="export_data_action", function=export_data())],
            ),
        ],
        controls=[
            vm.Filter(id="filter_continent", column="continent", selector=vm.Dropdown(id="filter_continent_selector")),
            vm.Parameter(
                id="parameter_x",
                targets=["scatter_chart.x"],
                selector=vm.Dropdown(
                    id="parameter_x_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                ),
            ),
        ],
    )
    # TODO: Call the Dashboard._pre_build() method once the pages registration is moved into this method.
    yield Vizro().build(vm.Dashboard(pages=[page]))
    del dash.page_registry["test_page"]


@pytest.fixture
def managers_one_page_no_actions():
    """Instantiates managers with one "empty" page."""
    page = vm.Page(
        id="test_page_no_actions",
        title="Second page",
        components=[vm.Card(text="")],
    )
    # TODO: Call the Dashboard._pre_build() method once the pages registration is moved into this method.
    yield Vizro().build(vm.Dashboard(pages=[page]))
    del dash.page_registry["test_page_no_actions"]


class TestGetActionLoopComponents:
    """Tests getting required components for the action loop."""

    @pytest.mark.usefixtures("managers_one_page_no_actions")
    def test_no_components(self):
        result = _get_action_loop_components()
        assert result == []

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    def test_fundamental_components(self, fundamental_components):
        result = _get_action_loop_components()
        for component in fundamental_components:
            assert repr(component) in map(repr, result), f"Can't find component: {repr(component)} in: {repr(result)}"

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    @pytest.mark.parametrize(
        "gateway_components",
        [("test_page", "export_data_button", "filter_continent_selector", "parameter_x_selector")],
        indirect=True,
    )
    def test_gateway_components(self, gateway_components):
        result = _get_action_loop_components()
        for component in gateway_components:
            assert repr(component) in map(repr, result), f"Can't find component: {repr(component)} in: {repr(result)}"

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    @pytest.mark.parametrize(
        "action_trigger_components",
        [("test_page", "export_data_button", "filter_continent_selector", "parameter_x_selector")],
        indirect=True,
    )
    def test_action_trigger_components(self, action_trigger_components):
        result = _get_action_loop_components()
        for component in action_trigger_components:
            assert repr(component) in map(repr, result), f"Can't find component: {repr(component)} in: {repr(result)}"

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    @pytest.mark.parametrize(
        "action_trigger_actions_id_component",
        [("test_page", "export_data_button", "filter_continent_selector", "parameter_x_selector")],
        indirect=True,
    )
    def test_action_trigger_actions_id_component(self, action_trigger_actions_id_component):
        result = _get_action_loop_components()
        for component in action_trigger_actions_id_component:
            assert repr(component) in map(repr, result), f"Can't find component: {repr(component)} in: {repr(result)}"

    @pytest.mark.usefixtures("managers_one_page_two_components_two_controls")
    @pytest.mark.parametrize(
        "trigger_to_actions_chain_mapper_component",
        [("test_page", "export_data_button", "filter_continent_selector", "parameter_x_selector")],
        indirect=True,
    )
    def test_trigger_to_actions_chain_mapper_component(self, trigger_to_actions_chain_mapper_component):
        result = _get_action_loop_components()
        for component in trigger_to_actions_chain_mapper_component:
            assert repr(component) in map(repr, result), f"Can't find component: {repr(component)} in: {repr(result)}"
