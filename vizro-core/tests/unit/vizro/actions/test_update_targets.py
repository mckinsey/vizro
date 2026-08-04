import pytest

import vizro.models as vm
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
        with pytest.raises(ValueError, match="targets {'invalid_target'} are not valid figures on the page."):
            action.pre_build()


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
