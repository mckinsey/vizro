import plotly.express as px
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
def callback_context_filter_interaction(request):
    """Mock dash.callback_context that represents a click on a continent data-point and table selected cell."""
    continent_filter_interaction, country_table_filter_interaction = request.param

    args_grouping_filter_interaction = []
    if continent_filter_interaction:
        args_grouping_filter_interaction.append(
            {
                "clickData": CallbackTriggerDict(
                    id="box_chart",
                    property="clickData",
                    value={
                        "points": [
                            {
                                "customdata": [continent_filter_interaction],
                            }
                        ]
                    },
                    str_id="box_chart",
                    triggered=False,
                )
            }
        )
    if country_table_filter_interaction:
        args_grouping_filter_interaction.append(
            {
                "active_cell": CallbackTriggerDict(
                    id="underlying_table_id",
                    property="active_cell",
                    value={"row": 0, "column": 0, "column_id": "country"},
                    str_id="underlying_table_id",
                    triggered=False,
                ),
                "derived_viewport_data": CallbackTriggerDict(
                    id="underlying_table_id",
                    property="derived_viewport_data",
                    value=[
                        {
                            "country": country_table_filter_interaction,
                            "continent": "Africa",
                            "year": 2007,
                        },
                        {
                            "country": "Egypt",
                            "continent": "Africa",
                            "year": 2007,
                        },
                    ],
                    str_id="underlying_table_id",
                    triggered=False,
                ),
            }
        )

    mock_callback_context = {
        "args_grouping": {
            "filters": [],
            "filter_interaction": args_grouping_filter_interaction,
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


@pytest.fixture
def target_scatter_filtered_continent(request, gapminder_2007, scatter_params):
    continent, country = request.param

    data = gapminder_2007
    if continent:
        data = data[data["continent"].isin([continent])]
    if country:
        data = data[data["country"].isin([country])]

    return px.scatter(data, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_box_filtered_continent(request, gapminder_2007, box_params):
    continent, country = request.param

    data = gapminder_2007
    if continent:
        data = data[data["continent"].isin([continent])]
    if country:
        data = data[data["country"].isin([country])]

    return px.box(data, **box_params).update_layout(margin_t=24)


@pytest.mark.usefixtures("managers_one_page_two_graphs_one_table_one_button")
class TestFilterInteraction:
    @pytest.mark.parametrize("callback_context_filter_interaction", [("Africa", None), ("Europe", None)], indirect=True)
    def test_filter_interaction_without_targets_temporary_behavior(  # temporary fix, see below test
        self,
        callback_context_filter_interaction,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["box_chart"].actions = [vm.Action(id="test_action", function=filter_interaction())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result == {}

    @pytest.mark.xfail  # This is the desired behavior, ie when no target is provided, then all charts filtered
    @pytest.mark.parametrize(
        "callback_context_filter_interaction," "target_scatter_filtered_continent," "target_box_filtered_continent",
        [
            (("Africa", None), ("Africa", None), ("Africa", None)),
            (("Europe", None), ("Europe", None), ("Europe", None)),
            (("Americas", None), ("Americas", None), ("Americas", None)),
        ],
        indirect=True,
    )
    def test_filter_interaction_without_targets_desired_behavior(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["box_chart"].actions = [vm.Action(id="test_action", function=filter_interaction())]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_interaction,target_scatter_filtered_continent",
        [
            (("Africa", None), ("Africa", None)),
            (("Europe", None), ("Europe", None)),
            (("Americas", None), ("Americas", None)),
        ],
        indirect=True,
    )
    def test_filter_interaction_with_one_target(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["box_chart"].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart"]))
        ]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_interaction,target_scatter_filtered_continent,target_box_filtered_continent",
        [
            (("Africa", None), ("Africa", None), ("Africa", None)),
            (("Europe", None), ("Europe", None), ("Europe", None)),
            (("Americas", None), ("Americas", None), ("Americas", None)),
        ],
        indirect=True,
    )
    def test_filter_interaction_with_two_target(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Add action to relevant component - here component[0] is the source_chart
        model_manager["box_chart"].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.xfail  # This (or similar code) should raise a Value/Validation error explaining next steps
    @pytest.mark.parametrize("target", ["scatter_chart", ["scatter_chart"]])
    @pytest.mark.parametrize("callback_context_filter_interaction", [("Africa", None), ("Europe", None)], indirect=True)
    def test_filter_interaction_with_invalid_targets(
        self,
        target,
        callback_context_filter_interaction,
    ):
        with pytest.raises(ValueError, match="Target invalid_target not found in model_manager."):
            # Add action to relevant component - here component[0] is the source_chart
            model_manager["box_chart"].actions = [
                vm.Action(id="test_action", function=filter_interaction(targets=target))
            ]

    @pytest.mark.parametrize(
        "callback_context_filter_interaction,target_scatter_filtered_continent",
        [
            ((None, "Algeria"), (None, "Algeria")),
            ((None, "Albania"), (None, "Albania")),
            ((None, "Argentina"), (None, "Argentina")),
        ],
        indirect=True,
    )
    def test_table_filter_interaction_with_one_target(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
    ):
        model_manager["box_chart"].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart"]))
        ]

        model_manager["vizro_table"].actions = [vm.Action(function=filter_interaction(targets=["scatter_chart"]))]
        model_manager["vizro_table"].pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_interaction, target_scatter_filtered_continent, target_box_filtered_continent",
        [
            ((None, "Algeria"), (None, "Algeria"), (None, "Algeria")),
            ((None, "Albania"), (None, "Albania"), (None, "Albania")),
            ((None, "Argentina"), (None, "Argentina"), (None, "Argentina")),
        ],
        indirect=True,
    )
    def test_table_filter_interaction_with_two_targets(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        model_manager["box_chart"].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]

        model_manager["vizro_table"].actions = [
            vm.Action(function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]
        model_manager["vizro_table"].pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_interaction, target_scatter_filtered_continent, target_box_filtered_continent",
        [
            (("Africa", "Algeria"), ("Africa", "Algeria"), ("Africa", "Algeria")),
            (("Europe", "Albania"), ("Europe", "Albania"), ("Europe", "Albania")),
            (("Americas", "Argentina"), ("Americas", "Argentina"), ("Americas", "Argentina")),
        ],
        indirect=True,
    )
    def test_mixed_chart_and_table_filter_interaction_with_two_targets(
        self,
        callback_context_filter_interaction,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        model_manager["box_chart"].actions = [
            vm.Action(id="test_action", function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]

        model_manager["vizro_table"].actions = [
            vm.Action(function=filter_interaction(targets=["scatter_chart", "box_chart"]))
        ]
        model_manager["vizro_table"].pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    # TODO: Simplify parametrization, such that we have less repetitive code
    # TODO: Eliminate above xfails
    # TODO: Complement tests above with backend tests (currently the targets are also taken from model_manager!
    # see _get_action_callback_mapping eg.)
