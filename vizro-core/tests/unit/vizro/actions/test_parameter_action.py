import pytest
from asserts import assert_component_equal
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
import vizro.plotly.express as px
from vizro._constants import PARAMETER_ACTION_PREFIX
from vizro.actions._actions_utils import CallbackTriggerDict
from vizro.managers import data_manager, model_manager


@pytest.fixture
def target_scatter_parameter_y(request, gapminder_2007, scatter_params):
    y = request.param
    scatter_params["y"] = y
    return px.scatter(gapminder_2007, **scatter_params)


@pytest.fixture
def target_scatter_matrix_parameter_dimensions(request, iris, scatter_matrix_params):
    dimensions = request.param
    scatter_matrix_params["dimensions"] = dimensions
    return px.scatter_matrix(iris, **scatter_matrix_params)


@pytest.fixture
def target_scatter_parameter_hover_data(request, gapminder_2007, scatter_params):
    hover_data = request.param
    scatter_params["hover_data"] = hover_data
    return px.scatter(gapminder_2007, **scatter_params)


@pytest.fixture
def target_box_parameter_y(request, gapminder_2007, box_params):
    y = request.param
    box_params["y"] = y
    return px.box(gapminder_2007, **box_params)


@pytest.fixture
def target_scatter_parameter_y_and_x(request, gapminder_2007, scatter_params):
    y, x = request.param
    scatter_params["y"] = y
    scatter_params["x"] = x
    return px.scatter(gapminder_2007, **scatter_params)


@pytest.fixture
def target_scatter_parameter_data_frame_first_n_last_n(
    request, gapminder_dynamic_first_n_last_n_function, scatter_params
):
    first_n_last_n_args = request.param
    return px.scatter(gapminder_dynamic_first_n_last_n_function(**first_n_last_n_args), **scatter_params)


@pytest.fixture
def target_box_parameter_data_frame_first_n_last_n(request, gapminder_dynamic_first_n_last_n_function, box_params):
    first_n_last_n_args = request.param
    return px.box(gapminder_dynamic_first_n_last_n_function(**first_n_last_n_args), **box_params)


@pytest.fixture
def target_box_parameter_y_and_x(request, gapminder_2007, box_params):
    y, x = request.param
    box_params["y"] = y
    box_params["x"] = x
    return px.box(gapminder_2007, **box_params)


@pytest.fixture
def ctx_parameter_y(request):
    """Mock dash.ctx that represents y-axis Parameter value selection."""
    y = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
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
                }
            }
        }
    }
    context_value.set(AttributeDict(**mock_ctx))
    return context_value


@pytest.fixture
def ctx_parameter_dimensions(request):
    """Mock dash.ctx that represents `dimensions` Parameter value selection."""
    y = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
                    "filter_interaction": [],
                    "filters": [],
                    "parameters": [
                        CallbackTriggerDict(
                            id="dimensions_parameter",
                            property="value",
                            value=y,
                            str_id="dimensions_parameter",
                            triggered=False,
                        )
                    ],
                }
            }
        }
    }
    context_value.set(AttributeDict(**mock_ctx))
    return context_value


@pytest.fixture
def ctx_parameter_hover_data(request):
    """Mock dash.ctx that represents hover_data Parameter value selection."""
    hover_data = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
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
                }
            }
        }
    }
    context_value.set(AttributeDict(**mock_ctx))
    return context_value


@pytest.fixture
def ctx_parameter_y_and_x(request):
    """Mock dash.ctx that represents y-axis Parameter value selection."""
    y, x = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
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
                }
            }
        }
    }
    context_value.set(AttributeDict(**mock_ctx))
    return context_value


@pytest.fixture
def ctx_parameter_data_frame_argument(request):
    """Mock dash.ctx that represents parameter applied."""
    targets, first_n_last_n_args = request.param

    dynamic_filters = []
    parameters = [
        CallbackTriggerDict(
            id="first_n_parameter",
            property="value",
            value=first_n_last_n_args["first_n"],
            str_id="first_n_parameter",
            triggered=False,
        )
    ]

    if last_n := first_n_last_n_args.get("last_n"):
        parameters.append(
            CallbackTriggerDict(
                id="last_n_parameter",
                property="value",
                value=last_n,
                str_id="last_n_parameter",
                triggered=False,
            )
        )

    if dynamic_filter_value := first_n_last_n_args.get("dynamic_filter_value"):
        dynamic_filters.append(
            CallbackTriggerDict(
                id="dynamic_filter_id_selector",
                property="value",
                value=dynamic_filter_value,
                str_id="dynamic_filter_id_selector",
                triggered=False,
            )
        )

    mock_ctx = {
        "args_grouping": {
            "external": {"_controls": {"filters": dynamic_filters, "filter_interaction": [], "parameters": parameters}}
        },
        "outputs_list": [
            {"id": {"action_id": "test_action", "target_id": target, "type": "download_dataframe"}, "property": "data"}
            for target in targets
        ],
    }

    context_value.set(AttributeDict(**mock_ctx))
    return context_value


class TestParameter:
    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_y, target_scatter_parameter_y",
        [("pop", "pop"), ("gdpPercap", "gdpPercap"), ("NONE", None)],
        indirect=True,
    )
    def test_one_parameter_one_target(self, ctx_parameter_y, target_scatter_parameter_y):
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_y}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_hover_data, target_scatter_parameter_hover_data",
        [
            ([], []),
            (["NONE"], [None]),
            (["NONE", "pop"], ["pop"]),
            (["NONE", "NONE"], [None]),
            (["ALL"], ["lifeExp", "pop", "gdpPercap"]),
            (["ALL", "lifeExp"], ["lifeExp", "pop", "gdpPercap"]),
            (["ALL", "NONE"], ["lifeExp", "pop", "gdpPercap"]),
        ],
        indirect=True,
    )
    def test_one_parameter_one_target_NONE_list(self, ctx_parameter_hover_data, target_scatter_parameter_hover_data):
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_hover_data}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_y, target_scatter_parameter_y, target_box_parameter_y",
        [("pop", "pop", "pop"), ("gdpPercap", "gdpPercap", "gdpPercap")],
        indirect=True,
    )
    def test_one_parameter_multiple_targets(self, ctx_parameter_y, target_scatter_parameter_y, target_box_parameter_y):
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_y, "box_chart": target_box_parameter_y}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_y_and_x, target_scatter_parameter_y_and_x",
        [(["pop", "continent"], ["pop", "continent"]), (["gdpPercap", "country"], ["gdpPercap", "country"])],
        indirect=True,
    )
    def test_multiple_parameters_one_target(self, ctx_parameter_y_and_x, target_scatter_parameter_y_and_x):
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_x"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_y_and_x}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x",
        [
            (["pop", "continent"], ["pop", "continent"], ["pop", "continent"]),
            (["gdpPercap", "country"], ["gdpPercap", "country"], ["gdpPercap", "country"]),
        ],
        indirect=True,
    )
    def test_multiple_parameters_multiple_targets(
        self, ctx_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_x"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_y_and_x, "box_chart": target_box_parameter_y_and_x}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x",
        [
            (["pop", "continent"], ["pop", "pop"], ["continent", "continent"]),
            (["gdpPercap", "country"], ["gdpPercap", "gdpPercap"], ["country", "country"]),
        ],
        indirect=True,
    )
    def test_one_parameter_per_target_multiple_attributes(
        self, ctx_parameter_y_and_x, target_scatter_parameter_y_and_x, target_box_parameter_y_and_x
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
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_scatter"].function(_controls=None)
        expected = {"scatter_chart": target_scatter_parameter_y_and_x}

        assert result == expected

        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_box"].function(_controls=None)
        expected = {"box_chart": target_box_parameter_y_and_x}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "ctx_parameter_data_frame_argument, target_scatter_parameter_data_frame_first_n_last_n",
        [
            ((["scatter_chart"], {"first_n": 50}), {"first_n": 50}),
            ((["scatter_chart"], {"first_n": 50, "last_n": 50}), {"first_n": 50, "last_n": 50}),
        ],
        indirect=True,
    )
    def test_data_frame_parameters_one_target(
        self,
        ctx_parameter_data_frame_argument,
        target_scatter_parameter_data_frame_first_n_last_n,
        gapminder_dynamic_first_n_last_n_function,
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        # Creating and adding a Parameter object (data_frame function argument parametrizing) to the existing Page
        first_n_parameter = vm.Parameter(
            id="test_data_frame_parameter",
            targets=["scatter_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(first_n_parameter)
        first_n_parameter.pre_build()

        # This parameter will affect results only if included in the ctx_parameter_data_frame_argument:
        last_n_parameter = vm.Parameter(
            id="test_data_frame_parameter_last_n",
            targets=["scatter_chart.data_frame.last_n"],
            selector=vm.Slider(id="last_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(last_n_parameter)
        last_n_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_data_frame_parameter"].function(_controls=None)

        expected = {
            "scatter_chart": target_scatter_parameter_data_frame_first_n_last_n,
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "ctx_parameter_data_frame_argument, "
        "target_scatter_parameter_data_frame_first_n_last_n, "
        "target_box_parameter_data_frame_first_n_last_n",
        [
            (
                (["scatter_chart", "box_chart"], {"first_n": 50}),
                {"first_n": 50},
                {"first_n": 50},
            ),
            (
                (["scatter_chart", "box_chart"], {"first_n": 50, "last_n": 50}),
                {"first_n": 50, "last_n": 50},
                {"first_n": 50, "last_n": 50},
            ),
        ],
        indirect=True,
    )
    def test_data_frame_parameters_multiple_targets(
        self,
        ctx_parameter_data_frame_argument,
        target_scatter_parameter_data_frame_first_n_last_n,
        target_box_parameter_data_frame_first_n_last_n,
        gapminder_dynamic_first_n_last_n_function,
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        # Creating and adding a Parameter object (data_frame function argument parametrizing) to the existing Page
        first_n_parameter = vm.Parameter(
            id="test_data_frame_parameter",
            targets=["scatter_chart.data_frame.first_n", "box_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(first_n_parameter)
        first_n_parameter.pre_build()

        # This parameter will affect results only if included in the ctx_parameter_data_frame_argument:
        last_n_parameter = vm.Parameter(
            id="test_data_frame_parameter_last_n",
            targets=["scatter_chart.data_frame.last_n", "box_chart.data_frame.last_n"],
            selector=vm.Slider(id="last_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(last_n_parameter)
        last_n_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_data_frame_parameter"].function(_controls=None)

        expected = {
            "scatter_chart": target_scatter_parameter_data_frame_first_n_last_n,
            "box_chart": target_box_parameter_data_frame_first_n_last_n,
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "ctx_parameter_data_frame_argument, "
        "target_scatter_parameter_data_frame_first_n_last_n, "
        "target_box_parameter_data_frame_first_n_last_n",
        [
            (
                (["scatter_chart", "box_chart"], {"first_n": 10, "dynamic_filter_value": ["Asia"]}),
                {"first_n": 10},
                {"first_n": 10},
            ),
        ],
        indirect=True,
    )
    def test_data_frame_parameters_one_target_and_one_filter(
        self,
        ctx_parameter_data_frame_argument,
        target_scatter_parameter_data_frame_first_n_last_n,
        target_box_parameter_data_frame_first_n_last_n,
        gapminder_dynamic_first_n_last_n_function,
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        # Creating and adding a dynamic Filter object to the existing Page
        dynamic_filter = vm.Filter(
            id="dynamic_filter_id",
            column="continent",
            targets=["scatter_chart", "box_chart"],
            selector=vm.Dropdown(id="dynamic_filter_id_selector"),
        )
        model_manager["test_page"].controls.append(dynamic_filter)
        dynamic_filter.pre_build()

        # Creating and adding a Parameter object (data_frame function argument parametrizing) to the existing Page
        first_n_parameter = vm.Parameter(
            id="test_data_frame_parameter",
            targets=["scatter_chart.data_frame.first_n", "box_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(first_n_parameter)
        first_n_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result_figures = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_data_frame_parameter"].function(_controls=None)

        # Result and expected dynamic filter object
        result_dynamic_filter = result_figures.pop("dynamic_filter_id")
        expected_dynamic_filter = dynamic_filter.selector(options=["Asia"])
        assert_component_equal(result_dynamic_filter, expected_dynamic_filter)

        expected_figures = {
            "scatter_chart": target_scatter_parameter_data_frame_first_n_last_n,
            "box_chart": target_box_parameter_data_frame_first_n_last_n,
        }

        assert result_figures == expected_figures

    @pytest.mark.usefixtures("managers_one_page_one_graph_with_dict_param_input")
    @pytest.mark.parametrize(
        "ctx_parameter_dimensions, target_scatter_matrix_parameter_dimensions",
        [("ALL", ["sepal_length", "sepal_width", "petal_length", "petal_width"]), (["sepal_width"], ["sepal_width"])],
        indirect=True,
    )
    def test_one_parameter_with_dict_input_as_options(
        self, ctx_parameter_dimensions, target_scatter_matrix_parameter_dimensions
    ):
        # If the options are provided as a list of dictionaries, the value should be correctly passed to the
        # target as a list. So when "ALL" is selected, a list of all possible values should be returned.
        dimensions_parameter = vm.Parameter(
            id="test_parameter_dimensions",
            targets=["scatter_matrix_chart.dimensions"],
            selector=vm.RadioItems(
                id="dimensions_parameter",
                options=[
                    {"label": "sepal_length", "value": "sepal_length"},
                    {"label": "sepal_width", "value": "sepal_width"},
                    {"label": "petal_length", "value": "petal_length"},
                    {"label": "petal_width", "value": "petal_width"},
                ],
            ),
        )
        model_manager["test_page"].controls = [dimensions_parameter]
        dimensions_parameter.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = model_manager[f"{PARAMETER_ACTION_PREFIX}_test_parameter_dimensions"].function(_controls=None)
        expected = {"scatter_matrix_chart": target_scatter_matrix_parameter_dimensions}

        assert result == expected
