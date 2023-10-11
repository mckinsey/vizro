import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
from vizro.actions import filter_interaction
from vizro.actions._actions_utils import (
    CallbackTriggerDict,
)
from vizro.managers import model_manager


@pytest.fixture
def callback_context_click_continent(request):
    """Mock dash.callback_context that represents a click on a continent data-point."""
    continent = request.param
    mock_callback_context = {
        "args_grouping": {
            "filters": [],
            "filter_interaction": [
                CallbackTriggerDict(
                    id="box_chart",
                    property="clickData",
                    value={
                        "points": [
                            {
                                "customdata": [continent],
                            }
                        ]
                    },
                    str_id="box_chart",
                    triggered=False,
                )
            ],
            "parameters": [],
            "theme_selector": CallbackTriggerDict(
                id="theme_selector",
                property="on",
                value=True,
                str_id="theme_selector",
                triggered=False,
            ),
        }
    }
    context_value.set(AttributeDict(**mock_callback_context))
    return context_value


@pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
class TestFilterInteraction:
    @pytest.mark.parametrize("callback_context_click_continent", ["Africa", "Europe"], indirect=True)
    def test_filter_interaction_without_targets_temporary_behavior(  # temporary fix, see below test
        self,
        callback_context_click_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["test_page"].components[0].actions = [vm.Action(id="test_action", function=filter_interaction())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result == {}

    @pytest.mark.xfail  # This is the desired behavior, ie when no target is provided, then all charts filtered
    @pytest.mark.parametrize(
        "callback_context_click_continent,target_scatter_filtered_continent,target_box_filtered_continent",
        [("Africa", "Africa", "Africa"), ("Europe", "Europe", "Europe"), ("Americas", "Americas", "Americas")],
        indirect=True,
    )
    def test_filter_interaction_without_targets_desired_behavior(
        self,
        callback_context_click_continent,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["test_page"].components[0].actions = [vm.Action(id="test_action", function=filter_interaction())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_click_continent,target_scatter_filtered_continent",
        [("Africa", ["Africa"]), ("Europe", ["Europe"]), ("Americas", ["Americas"])],
        indirect=True,
    )
    def test_filter_interaction_with_one_target(
        self,
        callback_context_click_continent,
        target_scatter_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["test_page"].components[0].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart"]))
        ]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_click_continent,target_scatter_filtered_continent,target_box_filtered_continent",
        [
            ("Africa", ["Africa"], ["Africa"]),
            ("Europe", ["Europe"], ["Europe"]),
            ("Americas", ["Americas"], ["Americas"]),
        ],
        indirect=True,
    )
    def test_filter_interaction_with_two_target(
        self,
        callback_context_click_continent,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["test_page"].components[0].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.xfail  # This (or similar code) should raise a Value/Validation error explaining next steps
    @pytest.mark.parametrize("target", ["scatter_chart", ["scatter_chart"]])
    @pytest.mark.parametrize("callback_context_click_continent", ["Africa", "Europe"], indirect=True)
    def test_filter_interaction_with_invalid_targets(
        self,
        target,
        callback_context_click_continent,
    ):
        with pytest.raises(ValueError, match="Target invalid_target not found in model_manager."):
            # Add action to relevant component - here component[0] is the source_chart
            model_manager["test_page"].components[0].actions = [
                vm.Action(id="test_action", function=filter_interaction(targets=target))
            ]

    # TODO: Simplify parametrization, such that we have less repetitive code
    # TODO: Eliminate above xfails
    # TODO: Complement tests above with backend tests (currently the targets are also taken from model_manager!
    # see _get_action_callback_mapping eg.)
