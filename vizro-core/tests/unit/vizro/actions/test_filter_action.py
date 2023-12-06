import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
import vizro.plotly.express as px
from vizro._constants import FILTER_ACTION_PREFIX
from vizro.actions._actions_utils import (
    CallbackTriggerDict,
)
from vizro.managers import model_manager


@pytest.fixture
def target_scatter_filtered_continent_and_pop(request, gapminder_2007, scatter_params):
    continent, pop = request.param
    data = gapminder_2007[
        gapminder_2007["continent"].isin(continent) & gapminder_2007["pop"].between(pop[0], pop[1], inclusive="both")
    ]
    return px.scatter(data, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_box_filtered_continent_and_pop(request, gapminder_2007, box_params):
    continent, pop = request.param
    data = gapminder_2007[
        gapminder_2007["continent"].isin(continent) & gapminder_2007["pop"].between(pop[0], pop[1], inclusive="both")
    ]
    return px.box(data, **box_params).update_layout(margin_t=24)


@pytest.fixture
def callback_context_filter_continent(request):
    """Mock dash.callback_context that represents continent Filter value selection."""
    continent = request.param
    mock_callback_context = {
        "args_grouping": {
            "filter_interaction": [],
            "filters": [
                CallbackTriggerDict(
                    id="continent_filter",
                    property="value",
                    value=continent,
                    str_id="continent_filter",
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


@pytest.fixture
def callback_context_filter_continent_and_pop(request):
    """Mock dash.callback_context that represents continent and pop Filter value selection."""
    continent, pop = request.param
    mock_callback_context = {
        "args_grouping": {
            "filter_interaction": [],
            "filters": [
                CallbackTriggerDict(
                    id="continent_filter",
                    property="value",
                    value=continent,
                    str_id="continent_filter",
                    triggered=False,
                ),
                CallbackTriggerDict(
                    id="pop_filter",
                    property="value",
                    value=pop,
                    str_id="pop_filter",
                    triggered=False,
                ),
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
class TestFilter:
    @pytest.mark.parametrize(
        "callback_context_filter_continent,target_scatter_filtered_continent,target_box_filtered_continent",
        [(["Africa"], ["Africa"], ["Africa"]), (["Africa", "Europe"], ["Africa", "Europe"], ["Africa", "Europe"])],
        indirect=True,
    )
    def test_one_filter_no_targets(
        self,
        callback_context_filter_continent,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Creating and adding a Filter object to the existing Page
        continent_filter = vm.Filter(id="test_filter", column="continent", selector=vm.Dropdown(id="continent_filter"))
        model_manager["test_page"].controls = [continent_filter]

        # Adds a default _filter Action to the "continent_filter" selector object
        continent_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_continent,target_scatter_filtered_continent",
        [(["Africa"], ["Africa"]), (["Africa", "Europe"], ["Africa", "Europe"])],
        indirect=True,
    )
    def test_one_filter_one_target(
        self,
        callback_context_filter_continent,
        target_scatter_filtered_continent,
    ):
        # Creating and adding a Filter object to the existing Page
        continent_filter = vm.Filter(
            id="test_filter", column="continent", targets=["scatter_chart"], selector=vm.Dropdown(id="continent_filter")
        )
        model_manager["test_page"].controls = [continent_filter]

        # Adds a default _filter Action to the "continent_filter" selector object
        continent_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert "box_chart" not in result

    @pytest.mark.parametrize(
        "callback_context_filter_continent,target_scatter_filtered_continent,target_box_filtered_continent",
        [(["Africa"], ["Africa"], ["Africa"]), (["Africa", "Europe"], ["Africa", "Europe"], ["Africa", "Europe"])],
        indirect=True,
    )
    def test_one_filter_multiple_targets(
        self,
        callback_context_filter_continent,
        target_scatter_filtered_continent,
        target_box_filtered_continent,
    ):
        # Creating and adding a Filter object to the existing Page
        continent_filter = vm.Filter(
            id="test_filter",
            column="continent",
            targets=["scatter_chart", "box_chart"],
            selector=vm.Dropdown(id="continent_filter"),
        )
        model_manager["test_page"].controls = [continent_filter]

        # Adds a default _filter Action to the "continent_filter" selector object
        continent_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent
        assert result["box_chart"] == target_box_filtered_continent

    @pytest.mark.parametrize(
        "callback_context_filter_continent_and_pop,target_scatter_filtered_continent_and_pop,target_box_filtered_continent_and_pop",
        [
            ([["Africa"], [10**6, 10**7]], [["Africa"], [10**6, 10**7]], [["Africa"], [10**6, 10**7]]),
            (
                [["Africa", "Europe"], [10**6, 10**7]],
                [["Africa", "Europe"], [10**6, 10**7]],
                [["Africa", "Europe"], [10**6, 10**7]],
            ),
        ],
        indirect=True,
    )
    def test_multiple_filters_no_targets(
        self,
        callback_context_filter_continent_and_pop,
        target_scatter_filtered_continent_and_pop,
        target_box_filtered_continent_and_pop,
    ):
        # Creating and adding a Filter objects to the existing Page
        continent_filter = vm.Filter(
            id="test_filter_continent", column="continent", selector=vm.Dropdown(id="continent_filter")
        )
        pop_filter = vm.Filter(id="test_filter_pop", column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [continent_filter, pop_filter]

        # Adds a default _filter Action to the filter selector objects
        continent_filter.pre_build()
        pop_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter_continent"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent_and_pop
        assert result["box_chart"] == target_box_filtered_continent_and_pop

    @pytest.mark.parametrize(
        "callback_context_filter_continent_and_pop,target_scatter_filtered_continent_and_pop",
        [
            ([["Africa"], [10**6, 10**7]], [["Africa"], [10**6, 10**7]]),
            ([["Africa", "Europe"], [10**6, 10**7]], [["Africa", "Europe"], [10**6, 10**7]]),
        ],
        indirect=True,
    )
    def test_multiple_filters_one_target(
        self,
        callback_context_filter_continent_and_pop,
        target_scatter_filtered_continent_and_pop,
    ):
        # Creating and adding a Filter objects to the existing Page
        continent_filter = vm.Filter(
            id="test_filter_continent",
            column="continent",
            targets=["scatter_chart"],
            selector=vm.Dropdown(id="continent_filter"),
        )
        pop_filter = vm.Filter(column="pop", targets=["scatter_chart"], selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [continent_filter, pop_filter]

        # Adds a default _filter Action to the filter selector objects
        continent_filter.pre_build()
        pop_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter_continent"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent_and_pop
        assert "box_chart" not in result

    @pytest.mark.parametrize(
        "callback_context_filter_continent_and_pop,target_scatter_filtered_continent_and_pop,target_box_filtered_continent_and_pop",
        [
            ([["Africa"], [10**6, 10**7]], [["Africa"], [10**6, 10**7]], [["Africa"], [10**6, 10**7]]),
            (
                [["Africa", "Europe"], [10**6, 10**7]],
                [["Africa", "Europe"], [10**6, 10**7]],
                [["Africa", "Europe"], [10**6, 10**7]],
            ),
        ],
        indirect=True,
    )
    def test_multiple_filters_multiple_targets(
        self,
        callback_context_filter_continent_and_pop,
        target_scatter_filtered_continent_and_pop,
        target_box_filtered_continent_and_pop,
    ):
        # Creating and adding a Filter objects to the existing Page
        continent_filter = vm.Filter(
            id="test_filter_continent",
            column="continent",
            targets=["scatter_chart", "box_chart"],
            selector=vm.Dropdown(id="continent_filter"),
        )
        pop_filter = vm.Filter(
            id="test_filter_pop",
            column="pop",
            targets=["scatter_chart", "box_chart"],
            selector=vm.RangeSlider(id="pop_filter"),
        )
        model_manager["test_page"].controls = [continent_filter, pop_filter]

        # Adds a default _filter Action to the filter selector objects
        continent_filter.pre_build()
        pop_filter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{FILTER_ACTION_PREFIX}_test_filter_continent"].function()

        assert result["scatter_chart"] == target_scatter_filtered_continent_and_pop
        assert result["box_chart"] == target_box_filtered_continent_and_pop
