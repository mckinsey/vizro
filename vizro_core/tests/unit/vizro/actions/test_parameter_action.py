import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
import vizro.plotly.express as px
from vizro._constants import PARAMETER_ACTION_PREFIX
from vizro.actions._actions_utils import (
    CallbackTriggerDict,
)
from vizro.managers import model_manager


@pytest.fixture
def target_scatter_parameter_y(request, gapminder_2007, scatter_params):
    y = request.param
    scatter_params["y"] = y
    return px.scatter(gapminder_2007, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_scatter_parameter_hover_data(request, gapminder_2007, scatter_params):
    hover_data = request.param
    scatter_params["hover_data"] = hover_data
    return px.scatter(gapminder_2007, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_box_parameter_y(request, gapminder_2007, box_params):
    y = request.param
    box_params["y"] = y
    return px.box(gapminder_2007, **box_params).update_layout(margin_t=24)


@pytest.fixture
def target_scatter_parameter_y_and_x(request, gapminder_2007, scatter_params):
    y, x = request.param
    scatter_params["y"] = y
    scatter_params["x"] = x
    return px.scatter(gapminder_2007, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_box_parameter_y_and_x(request, gapminder_2007, box_params):
    y, x = request.param
    box_params["y"] = y
    box_params["x"] = x
    return px.box(gapminder_2007, **box_params).update_layout(margin_t=24)


@pytest.fixture
def callback_context_parameter_y(request):
    """Mock dash.callback_context that represents y-axis Parameter value selection."""
    y = request.param
    mock_callback_context = {
        "args_grouping": {
            "filter_interaction": [],
            "filters": [],
            "parameters": [
                CallbackTriggerDict(
                    id="y_parameter",
                    property="value",
                    value=y,
                    str_id="y_parameter",
                    triggered=False,
                )
            ],
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
def callback_context_parameter_hover_data(request):
    """Mock dash.callback_context that represents hover_data Parameter value selection."""
    hover_data = request.param
    mock_callback_context = {
        "args_grouping": {
            "filter_interaction": [],
            "filters": [],
            "parameters": [
                CallbackTriggerDict(
                    id="hover_data_parameter",
                    property="value",
                    value=hover_data,
                    str_id="hover_data_parameter",
                    triggered=False,
                )
            ],
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
def callback_context_parameter_y_and_x(request):
    """Mock dash.callback_context that represents y-axis Parameter value selection."""
    y, x = request.param
    mock_callback_context = {
        "args_grouping": {
            "filter_interaction": [],
            "filters": [],
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
class TestParameter:
    @pytest.mark.parametrize(
        "callback_context_parameter_y, target_scatter_parameter_y",
        [("pop", "pop"), ("gdpPercap", "gdpPercap"), ("NONE", None)],
        indirect=True,
    )
    def test_one_parameter_one_target(
        self,
        callback_context_parameter_y,
        target_scatter_parameter_y,
    ):
        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter",
            targets=["scatter_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        model_manager["test_page"].controls = [y_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function()

        assert result["scatter_chart"] == target_scatter_parameter_y
        assert "box_chart" not in result

    @pytest.mark.parametrize(
        "callback_context_parameter_hover_data, target_scatter_parameter_hover_data",
        [
            (["NONE"], [None]),
            (["NONE", "pop"], ["pop"]),
            (["NONE", "NONE"], [None]),
            (["ALL"], ["lifeExp", "pop", "gdpPercap"]),
            (["ALL", "lifeExp"], ["lifeExp", "pop", "gdpPercap"]),
            (["ALL", "NONE"], ["lifeExp", "pop", "gdpPercap"]),
        ],
        indirect=True,
    )
    def test_one_parameter_one_target_NONE_list(
        self,
        callback_context_parameter_hover_data,
        target_scatter_parameter_hover_data,
    ):
        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter",
            targets=["scatter_chart.hover_data"],
            selector=vm.Dropdown(
                id="hover_data_parameter", multi=True, options=["NONE", "lifeExp", "pop", "gdpPercap"], value=["NONE"]
            ),
        )
        model_manager["test_page"].controls = [y_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function()

        assert result["scatter_chart"] == target_scatter_parameter_hover_data
        assert "box_chart" not in result

    @pytest.mark.parametrize(
        "callback_context_parameter_y, target_scatter_parameter_y, target_box_parameter_y",
        [("pop", "pop", "pop"), ("gdpPercap", "gdpPercap", "gdpPercap")],
        indirect=True,
    )
    def test_one_parameter_multiple_targets(
        self,
        callback_context_parameter_y,
        target_scatter_parameter_y,
        target_box_parameter_y,
    ):
        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter",
            targets=["scatter_chart.y", "box_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        model_manager["test_page"].controls = [y_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function()

        assert result["scatter_chart"] == target_scatter_parameter_y
        assert result["box_chart"] == target_box_parameter_y

    @pytest.mark.parametrize(
        "callback_context_parameter_y_and_x, target_scatter_parameter_y_and_x",
        [(["pop", "continent"], ["pop", "continent"]), (["gdpPercap", "country"], ["gdpPercap", "country"])],
        indirect=True,
    )
    def test_multiple_parameters_one_target(
        self,
        callback_context_parameter_y_and_x,
        target_scatter_parameter_y_and_x,
    ):
        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter_x",
            targets=["scatter_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        x_parameter = vm.Parameter(
            id="test_parameter_y",
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(id="x_parameter", options=["continent", "country"], value="continent"),
        )
        model_manager["test_page"].controls = [y_parameter, x_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()
        x_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_x"].function()

        assert result["scatter_chart"] == target_scatter_parameter_y_and_x
        assert "box_chart" not in result

    @pytest.mark.parametrize(
        "callback_context_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x",
        [
            (["pop", "continent"], ["pop", "continent"], ["pop", "continent"]),
            (["gdpPercap", "country"], ["gdpPercap", "country"], ["gdpPercap", "country"]),
        ],
        indirect=True,
    )
    def test_multiple_parameters_multiple_targets(
        self,
        callback_context_parameter_y_and_x,
        target_scatter_parameter_y_and_x,
        target_box_parameter_y_and_x,
    ):
        # Creating and adding a Parameter object to the existing Page
        y_parameter = vm.Parameter(
            id="test_parameter_x",
            targets=["scatter_chart.y", "box_chart.y"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        x_parameter = vm.Parameter(
            id="test_parameter_y",
            targets=["scatter_chart.x", "box_chart.x"],
            selector=vm.RadioItems(id="x_parameter", options=["continent", "country"], value="continent"),
        )
        model_manager["test_page"].controls = [y_parameter, x_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        y_parameter.pre_build()
        x_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_x"].function()

        assert result["scatter_chart"] == target_scatter_parameter_y_and_x
        assert result["box_chart"] == target_box_parameter_y_and_x

    @pytest.mark.parametrize(
        "callback_context_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x",
        [
            (["pop", "continent"], ["pop", "pop"], ["continent", "continent"]),
            (["gdpPercap", "country"], ["gdpPercap", "gdpPercap"], ["country", "country"]),
        ],
        indirect=True,
    )
    def test_one_parameter_per_target_multiple_attributes(
        self,
        callback_context_parameter_y_and_x,
        target_scatter_parameter_y_and_x,
        target_box_parameter_y_and_x,
    ):
        # Creating and adding a Parameter object to the existing Page
        scatter_parameter = vm.Parameter(
            id="test_parameter_scatter",
            targets=["scatter_chart.y", "scatter_chart.x"],
            selector=vm.RadioItems(id="y_parameter", options=["lifeExp", "pop", "gdpPercap"], value="lifeExp"),
        )
        box_parameter = vm.Parameter(
            id="test_parameter_box",
            targets=["box_chart.y", "box_chart.x"],
            selector=vm.RadioItems(id="x_parameter", options=["continent", "country"], value="continent"),
        )
        model_manager["test_page"].controls = [scatter_parameter, box_parameter]

        # Adds a default _parameter Action to the "y_parameter" selector object
        scatter_parameter.pre_build()
        box_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_scatter"].function()
        assert result["scatter_chart"] == target_scatter_parameter_y_and_x
        assert "box_chart" not in target_scatter_parameter_y_and_x

        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_box"].function()
        assert result["box_chart"] == target_box_parameter_y_and_x
        assert "scatter_chart" not in target_scatter_parameter_y_and_x
