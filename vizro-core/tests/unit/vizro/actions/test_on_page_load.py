import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
import vizro.plotly.express as px
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions._actions_utils import CallbackTriggerDict
from vizro.managers import model_manager


@pytest.fixture
def target_scatter_filtered_continent_and_pop_parameter_y_and_x(request, gapminder_2007, scatter_params):
    continent, pop, y, x = request.param
    continent = continent if isinstance(continent, list) else [continent]
    data = gapminder_2007[
        gapminder_2007["continent"].isin(continent) & gapminder_2007["pop"].between(pop[0], pop[1], inclusive="both")
    ]
    scatter_params["y"] = y
    scatter_params["x"] = x
    return px.scatter(data, **scatter_params)


@pytest.fixture
def target_box_filtered_continent_and_pop_parameter_y_and_x(request, gapminder_2007, box_params):
    continent, pop, y, x = request.param
    continent = continent if isinstance(continent, list) else [continent]
    data = gapminder_2007[
        gapminder_2007["continent"].isin(continent) & gapminder_2007["pop"].between(pop[0], pop[1], inclusive="both")
    ]
    box_params["y"] = y
    box_params["x"] = x
    return px.box(data, **box_params)


@pytest.fixture
def ctx_on_page_load(request):
    """Mock dash.ctx that represents on page load."""
    continent_filter, pop, y, x = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
                    "filter_interaction": [],
                    "filters": [
                        CallbackTriggerDict(
                            id="continent_filter",
                            property="value",
                            value=continent_filter,
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
                    "parameters": [
                        CallbackTriggerDict(
                            id="y_parameter",
                            property="value",
                            value=y,
                            str_id="y_parameter",
                            triggered=False,
                        ),
                        CallbackTriggerDict(
                            id="x_parameter",
                            property="value",
                            value=x,
                            str_id="x_parameter",
                            triggered=False,
                        ),
                    ],
                }
            }
        }
    }
    context_value.set(AttributeDict(**mock_ctx))
    return context_value


# These tests only have one case in the pytest.mark.parametrize but have been left as parametrized so that they can
# use fixtures with `indirect` and `request.param` in order to match other tests.
class TestOnPageLoad:
    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_on_page_load, target_scatter_filtered_continent_and_pop_parameter_y_and_x",
        [
            (
                ["Africa", [10**6, 10**7], "pop", "continent"],
                ["Africa", [10**6, 10**7], "pop", "continent"],
            ),
        ],
        indirect=["ctx_on_page_load", "target_scatter_filtered_continent_and_pop_parameter_y_and_x"],
    )
    def test_multiple_controls_one_target(
        self, ctx_on_page_load, target_scatter_filtered_continent_and_pop_parameter_y_and_x, box_chart
    ):
        # Creating and adding a Filter objects to the existing Page
        continent_filter = vm.Filter(
            id="test_filter_continent",
            column="continent",
            targets=["scatter_chart"],
            selector=vm.Dropdown(id="continent_filter"),
        )
        pop_filter = vm.Filter(
            id="test_filter_pop", column="pop", targets=["scatter_chart"], selector=vm.RangeSlider(id="pop_filter")
        )
        model_manager["test_page"].controls = [continent_filter, pop_filter]

        # Adds a default _filter Action to the filter selector objects
        continent_filter.pre_build()
        pop_filter.pre_build()

        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter_y",
            targets=["scatter_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        x_parameter = vm.Parameter(
            id="test_parameter_x",
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(id="x_parameter", options=["continent", "country"], value="continent"),
        )
        model_manager["test_page"].controls = [y_parameter, x_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()
        x_parameter.pre_build()

        # Run action by picking 'on_page_load' default Page action function and executing it with ()
        result = model_manager[f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_test_page"].function(_controls=None)

        expected = {
            "scatter_chart": target_scatter_filtered_continent_and_pop_parameter_y_and_x,
            "box_chart": box_chart,
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_on_page_load, "
        "target_scatter_filtered_continent_and_pop_parameter_y_and_x, "
        "target_box_filtered_continent_and_pop_parameter_y_and_x",
        [
            (
                ["Africa", [10**6, 10**7], "pop", "continent"],
                ["Africa", [10**6, 10**7], "pop", "continent"],
                ["Africa", [10**6, 10**7], "pop", "continent"],
            ),
        ],
        indirect=True,
    )
    def test_multiple_controls_multiple_targets(
        self,
        ctx_on_page_load,
        target_scatter_filtered_continent_and_pop_parameter_y_and_x,
        target_box_filtered_continent_and_pop_parameter_y_and_x,
    ):
        # Creating and adding a Filter objects to the existing Page
        continent_filter = vm.Filter(
            column="continent", targets=["scatter_chart", "box_chart"], selector=vm.Dropdown(id="continent_filter")
        )
        pop_filter = vm.Filter(
            column="pop", targets=["scatter_chart", "box_chart"], selector=vm.RangeSlider(id="pop_filter")
        )
        model_manager["test_page"].controls = [continent_filter, pop_filter]

        # Adds a default _filter Action to the filter selector objects
        continent_filter.pre_build()
        pop_filter.pre_build()

        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            targets=["scatter_chart.y", "box_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        x_parameter = vm.Parameter(
            targets=["scatter_chart.x", "box_chart.x"],
            selector=vm.RadioItems(id="x_parameter", options=["continent", "country"], value="continent"),
        )
        model_manager["test_page"].controls = [y_parameter, x_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()
        x_parameter.pre_build()

        # Run action by picking 'on_page_load' default Page action function and executing it with ()
        result = model_manager[f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_test_page"].function(_controls=None)
        expected = {
            "scatter_chart": target_scatter_filtered_continent_and_pop_parameter_y_and_x,
            "box_chart": target_box_filtered_continent_and_pop_parameter_y_and_x,
        }

        assert result == expected
