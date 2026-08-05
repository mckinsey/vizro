import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import update_targets
from vizro.managers import model_manager


@pytest.fixture
def managers_page_two_graphs_button(box_chart, scatter_chart):
    """A page with two graphs and a button whose action is a bare `update_targets` (targets resolved in pre_build)."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="box_chart", figure=box_chart),
            vm.Graph(id="scatter_chart", figure=scatter_chart),
            vm.Button(id="button", actions=update_targets(id="update_targets_action")),
        ],
    )


class TestUpdateTargetsInstantiation:
    def test_create_update_targets_mandatory_only(self):
        action = update_targets(id="action_test")
        assert action.targets == []
        assert action.type == "update_targets"

    def test_create_update_targets_with_targets(self):
        action = update_targets(id="action_test", targets=["scatter_chart"])
        assert action.targets == ["scatter_chart"]


class TestUpdateTargetsPreBuild:
    def test_default_targets_are_all_figures_on_page(self, managers_page_two_graphs_button):
        Vizro._pre_build()
        action = model_manager["update_targets_action"]
        assert set(action.targets) == {"box_chart", "scatter_chart"}

    def test_explicit_targets_kept(self, managers_page_two_graphs_button):
        action = model_manager["update_targets_action"]
        action.targets = ["scatter_chart"]
        action.pre_build()
        assert action.targets == ["scatter_chart"]

    def test_invalid_targets_raise(self, managers_page_two_graphs_button):
        action = model_manager["update_targets_action"]
        action.targets = ["invalid_target"]
        with pytest.raises(ValueError, match=r"targets {'invalid_target'} are not valid targets on the page."):
            action.pre_build()

    def test_default_targets_include_dynamic_filters(self, gapminder_dynamic_first_n_last_n_function):
        # A bare update_targets() refreshes the whole page: figures + dynamic filters (mirrors on-page-load).
        from vizro.managers import data_manager

        data_manager["dynamic_df"] = gapminder_dynamic_first_n_last_n_function
        vm.Page(
            id="test_page",
            title="My first dashboard",
            components=[vm.Graph(id="dynamic_graph", figure=px.scatter("dynamic_df", x="gdpPercap", y="lifeExp"))],
            controls=[vm.Filter(id="dynamic_filter", column="continent", targets=["dynamic_graph"])],
        )
        model_manager["test_page"].components.append(vm.Button(id="button", actions=update_targets(id="ut_action")))
        Vizro._pre_build()

        assert model_manager["dynamic_filter"]._dynamic
        assert set(model_manager["ut_action"].targets) == {"dynamic_graph", "dynamic_filter"}


class TestUpdateTargetsOutputs:
    def test_outputs_figure_targets(self, managers_page_two_graphs_button):
        action = model_manager["update_targets_action"]
        action.targets = ["box_chart", "scatter_chart"]
        assert action.outputs == {"box_chart": "box_chart", "scatter_chart": "scatter_chart"}

    def test_outputs_filter_target_writes_to_selector(self, box_chart):
        # A (dynamic) filter is a valid target; its output must be routed to the selector so the whole filter isn't
        # replaced (which would reset the selected value).
        vm.Page(
            id="test_page",
            title="My first dashboard",
            components=[vm.Graph(id="box_chart", figure=box_chart)],
            controls=[vm.Filter(id="continent_filter", column="continent", targets=["box_chart"])],
        )
        action = update_targets(id="update_targets_action", targets=["box_chart", "continent_filter"])
        assert action.outputs == {"box_chart": "box_chart", "continent_filter": "continent_filter.selector"}


class TestUpdateTargetsRuntime:
    def test_dynamic_filter_only_target_does_not_crash(self, gapminder_dynamic_first_n_last_n_function):
        # Regression: targeting only a dynamic filter (no figure) must still load the filter's own targets' data so
        # its options can be recomputed, instead of crashing on empty data in Filter._validate_targeted_data.
        from vizro.actions._actions_utils import CallbackTriggerDict, _get_modified_page_figures
        from vizro.managers import data_manager

        data_manager["dynamic_df"] = gapminder_dynamic_first_n_last_n_function
        vm.Page(
            id="test_page",
            title="My first dashboard",
            components=[vm.Graph(id="dynamic_graph", figure=px.scatter("dynamic_df", x="gdpPercap", y="lifeExp"))],
            controls=[vm.Filter(id="dynamic_filter", column="continent", targets=["dynamic_graph"])],
        )
        Vizro._pre_build()

        selector_id = model_manager["dynamic_filter"].selector.id
        outputs = _get_modified_page_figures(
            ctds_filter=[
                CallbackTriggerDict(
                    id=selector_id, property="value", value=["Europe"], str_id=selector_id, triggered=False
                )
            ],
            ctds_filter_interaction=[],
            ctds_parameter=[],
            targets=["dynamic_filter"],
        )
        # The filter selector is rebuilt (no figure output), proving the filter's own target data was loaded.
        assert set(outputs) == {"dynamic_filter"}

    def test_empty_actions_filter_value_still_applies_on_refresh(self, gapminder):
        # A filter whose selector has empty actions does not refresh anything on its own, but its value must still be
        # applied whenever its target figure is refreshed by something else (e.g. a Button running update_targets,
        # simulated here by calling _get_modified_page_figures directly on the graph).
        from vizro.actions._actions_utils import CallbackTriggerDict, _get_modified_page_figures

        vm.Page(
            id="test_page",
            title="My first dashboard",
            components=[
                vm.Graph(id="graph", figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp", color="continent"))
            ],
            controls=[
                vm.Filter(
                    id="continent_filter",
                    column="continent",
                    targets=["graph"],
                    selector=vm.Dropdown(id="continent_selector", actions=[]),
                ),
            ],
        )
        Vizro._pre_build()
        assert model_manager["continent_filter"].selector.actions == []

        outputs = _get_modified_page_figures(
            ctds_filter=[
                CallbackTriggerDict(
                    id="continent_selector",
                    property="value",
                    value=["Europe"],
                    str_id="continent_selector",
                    triggered=False,
                )
            ],
            ctds_filter_interaction=[],
            ctds_parameter=[],
            targets=["graph"],
        )
        rendered_continents = {trace.legendgroup for trace in outputs["graph"].data if trace.legendgroup}
        assert rendered_continents == {"Europe"}

    def test_duplicate_figure_target_rebuilt_once(self, gapminder):
        # Regression: a Parameter targeting two args of the same figure yields update_targets(targets=["g", "g"]);
        # the figure must be rebuilt only once, not once per duplicate.
        from vizro.actions._actions_utils import _get_modified_page_figures
        from vizro.models.types import capture

        builds = {"n": 0}

        @capture("graph")
        def counting_fig(data_frame):
            builds["n"] += 1
            return px.scatter(data_frame, x="gdpPercap", y="lifeExp")

        vm.Page(id="test_page", title="t", components=[vm.Graph(id="g", figure=counting_fig(data_frame=gapminder))])
        Vizro._pre_build()

        builds["n"] = 0
        outputs = _get_modified_page_figures(
            ctds_filter=[], ctds_filter_interaction=[], ctds_parameter=[], targets=["g", "g"]
        )
        assert set(outputs) == {"g"}
        assert builds["n"] == 1

    def test_control_states_collected_regardless_of_selector_actions(self, gapminder, identity_action_function):
        # Regression guard for the always-apply contract: _get_control_states must collect ALL page filters/parameters
        # regardless of their selector.actions (empty or custom), else deferred/custom controls silently stop applying
        # when their targets are refreshed by another action.
        from vizro.models import Filter, Parameter

        custom_action = vm.Action(function=identity_action_function())
        vm.Page(
            id="test_page",
            title="t",
            components=[vm.Graph(id="graph", figure=px.scatter(gapminder, x="gdpPercap", y="lifeExp"))],
            controls=[
                vm.Filter(
                    id="empty_filter",
                    column="continent",
                    targets=["graph"],
                    selector=vm.Dropdown(id="empty_filter_sel", actions=[]),
                ),
                vm.Parameter(
                    id="custom_param",
                    targets=["graph.x"],
                    selector=vm.Dropdown(id="custom_param_sel", options=["gdpPercap", "pop"], actions=[custom_action]),
                ),
            ],
        )
        Vizro._pre_build()

        opl_action = model_manager["test_page"].actions[0]
        filter_ids = {state.component_id for state in opl_action._get_control_states(Filter)}
        param_ids = {state.component_id for state in opl_action._get_control_states(Parameter)}
        assert "empty_filter_sel" in filter_ids
        assert "custom_param_sel" in param_ids
