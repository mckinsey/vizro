import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import vizro.models as vm
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.actions._actions_utils import CallbackTriggerDict
from vizro.managers import data_manager, model_manager


@pytest.fixture
def target_data_filter_and_filter_interaction(request, gapminder_2007):
    pop_filter, continent_filter_interaction, country_table_filter_interaction = request.param
    data = gapminder_2007
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    if continent_filter_interaction:
        data = data[data["continent"].isin(continent_filter_interaction)]
    if country_table_filter_interaction:
        data = data[data["country"].isin(country_table_filter_interaction)]
    return data


@pytest.fixture
def target_data_filter_and_parameter(request, gapminder):
    pop_filter, first_n_parameter = request.param
    data = gapminder
    if first_n_parameter:
        data = data.head(first_n_parameter)
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    return data


@pytest.fixture
def target_data_filtered_pop(request, gapminder_2007):
    pop_filter = request.param
    data = gapminder_2007
    if pop_filter:
        data = data[data["pop"].between(pop_filter[0], pop_filter[1], inclusive="both")]
    return data


@pytest.fixture
def managers_one_page_without_graphs_one_button():
    """Instantiates a simple model_manager and data_manager with a page, and no graphs."""
    vm.Page(id="test_page", title="My first dashboard", components=[vm.Button(id="button")])
    Vizro._pre_build()


@pytest.fixture
def ctx_export_data(request):
    """Mock dash.ctx that represents filters and filter interactions applied."""
    targets, pop_filter, continent_filter_interaction, country_table_filter_interaction = request.param
    args_grouping_filter_interaction = []
    if continent_filter_interaction:
        args_grouping_filter_interaction.append(
            {
                "clickData": CallbackTriggerDict(
                    id="box_chart",
                    property="clickData",
                    value={"points": [{"customdata": [continent_filter_interaction]}]},
                    str_id="box_chart",
                    triggered=False,
                ),
                "modelID": CallbackTriggerDict(
                    id="box_chart", property="id", value="box_chart", str_id="box_chart", triggered=False
                ),
            },
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
                        {"country": "Algeria", "continent": "Africa", "year": 2007},
                        {"country": "Egypt", "continent": "Africa", "year": 2007},
                    ],
                    str_id="underlying_table_id",
                    triggered=False,
                ),
                "modelID": CallbackTriggerDict(
                    id="vizro_table", property="id", value="vizro_table", str_id="vizro_table", triggered=False
                ),
            }
        )
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
                    "filters": (
                        [
                            CallbackTriggerDict(
                                id="pop_filter",
                                property="value",
                                value=pop_filter,
                                str_id="pop_filter",
                                triggered=False,
                            )
                        ]
                        if pop_filter
                        else []
                    ),
                    "parameters": [],
                    "filter_interaction": args_grouping_filter_interaction,
                }
            }
        },
        "outputs_list": [
            {"id": {"action_id": "test_action", "target_id": target, "type": "download_dataframe"}, "property": "data"}
            for target in targets
        ],
    }

    context_value.set(AttributeDict(**mock_ctx))
    return context_value


@pytest.fixture
def ctx_export_data_filter_and_parameter(request):
    """Mock dash.ctx that represents filters and parameter applied."""
    targets, pop_filter, first_n_parameter = request.param
    mock_ctx = {
        "args_grouping": {
            "external": {
                "_controls": {
                    "filters": (
                        [
                            CallbackTriggerDict(
                                id="pop_filter",
                                property="value",
                                value=pop_filter,
                                str_id="pop_filter",
                                triggered=False,
                            )
                        ]
                        if pop_filter
                        else []
                    ),
                    "parameters": (
                        [
                            CallbackTriggerDict(
                                id="first_n_parameter",
                                property="value",
                                value=first_n_parameter,
                                str_id="first_n_parameter",
                                triggered=False,
                            )
                        ]
                        if first_n_parameter
                        else []
                    ),
                    "filter_interaction": [],
                }
            }
        },
        "outputs_list": [
            {"id": {"action_id": "test_action", "target_id": target, "type": "download_dataframe"}, "property": "data"}
            for target in targets
        ],
    }

    context_value.set(AttributeDict(**mock_ctx))
    return context_value


class TestExportData:
    @pytest.mark.usefixtures("managers_one_page_without_graphs_one_button")
    @pytest.mark.parametrize("ctx_export_data", [([[], None, None, None])], indirect=True)
    def test_no_graphs_no_targets(self, ctx_export_data):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action")]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function(_controls=None)
        expected = {}

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("ctx_export_data", [([["scatter_chart", "box_chart"], None, None, None])], indirect=True)
    def test_graphs_no_targets(self, ctx_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action")]
        action = model_manager["test_action"]
        action.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = action.function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_export_data",
        [(["scatter_chart", "box_chart"], None, None, None)],
        indirect=True,
    )
    def test_graphs_false_targets(self, ctx_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action")]
        action = model_manager["test_action"]
        action.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = action.function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("ctx_export_data", [(["scatter_chart"], None, None, None)], indirect=True)
    def test_one_target(self, ctx_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["scatter_chart"])]
        action = model_manager["test_action"]
        action.pre_build()

        # Run action by picking the above added action function and executing it with ()
        result = action.function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            }
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("ctx_export_data", [(["scatter_chart", "box_chart"], None, None, None)], indirect=True)
    def test_multiple_targets(self, ctx_export_data, gapminder_2007):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["scatter_chart", "box_chart"])]

        # Run action by picking the above added action function and executing it with ()
        result = model_manager["test_action"].function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": gapminder_2007.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize("ctx_export_data", [(["invalid_target_id"], None, None, None)], indirect=True)
    def test_invalid_target(self, ctx_export_data):
        # Add action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["invalid_target_id"])]
        action = model_manager["test_action"]

        with pytest.raises(ValueError, match="targets {'invalid_target_id'} are not valid figures on the page."):
            action.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_button")
    @pytest.mark.parametrize(
        "ctx_export_data, target_data_filter_and_filter_interaction, target_data_filtered_pop",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None, None],
                [[10**6, 10**7], None, None],
                [10**6, 10**7],
            ),
            ([["scatter_chart", "box_chart"], None, "Africa", None], [None, ["Africa"], None], None),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], "Africa", None],
                [[10**6, 10**7], ["Africa"], None],
                [10**6, 10**7],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_filter_interaction(
        self, ctx_export_data, target_data_filter_and_filter_interaction, target_data_filtered_pop
    ):
        # Creating and adding a Filter object to the existing Page
        pop_filter = vm.Filter(column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [pop_filter]
        # Adds a default _filter Action to the filter selector objects
        pop_filter.pre_build()

        # Add filter_interaction Action to scatter_chart component
        model_manager["box_chart"].actions = [filter_interaction(id="filter_interaction", targets=["scatter_chart"])]

        # Add export_data action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["scatter_chart", "box_chart"])]

        # Run action by picking the above added export_data action function and executing it with ()
        result = model_manager["test_action"].function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": target_data_filter_and_filter_interaction.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": target_data_filtered_pop.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_one_table_one_aggrid_one_button")
    @pytest.mark.parametrize(
        "ctx_export_data, target_data_filter_and_filter_interaction, target_data_filtered_pop",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None, "Algeria"],
                [[10**6, 10**7], None, ["Algeria"]],
                [10**6, 10**7],
            ),
            ([["scatter_chart", "box_chart"], None, "Africa", "Algeria"], [None, ["Africa"], ["Algeria"]], None),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], "Africa", "Algeria"],
                [[10**6, 10**7], ["Africa"], ["Algeria"]],
                [10**6, 10**7],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_filter_interaction_and_table(
        self, ctx_export_data, target_data_filter_and_filter_interaction, target_data_filtered_pop
    ):
        # Creating and adding a Filter object to the existing Page
        pop_filter = vm.Filter(column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [pop_filter]
        # Adds a default _filter Action to the filter selector objects
        pop_filter.pre_build()

        # Add filter_interaction Action to scatter_chart component
        model_manager["box_chart"].actions = [filter_interaction(id="filter_interaction", targets=["scatter_chart"])]

        # Add table filter_interaction Action to scatter_chart component
        model_manager["vizro_table"].actions = [filter_interaction(targets=["scatter_chart"])]
        model_manager["vizro_table"].pre_build()

        # Add export_data action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["scatter_chart", "box_chart"])]

        # Run action by picking the above added export_data action function and executing it with ()
        result = model_manager["test_action"].function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": target_data_filter_and_filter_interaction.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": target_data_filtered_pop.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "ctx_export_data_filter_and_parameter, target_data_filter_and_parameter",
        [
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], None],
                [[10**6, 10**7], None],
            ),
            (
                [["scatter_chart", "box_chart"], None, 50],
                [None, 50],
            ),
            (
                [["scatter_chart", "box_chart"], [10**6, 10**7], 50],
                [[10**6, 10**7], 50],
            ),
        ],
        indirect=True,
    )
    def test_multiple_targets_with_filter_and_data_frame_parameter(
        self,
        ctx_export_data_filter_and_parameter,
        target_data_filter_and_parameter,
        gapminder_dynamic_first_n_last_n_function,
    ):
        # Adding dynamic data_frame to data_manager
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        # Creating and adding a Filter object to the existing Page
        pop_filter = vm.Filter(column="pop", selector=vm.RangeSlider(id="pop_filter"))
        model_manager["test_page"].controls = [pop_filter]
        # Adds a default _filter Action to the filter selector objects
        pop_filter.pre_build()

        # Creating and adding a Parameter object (data_frame function argument parametrizing) to the existing Page
        first_n_parameter = vm.Parameter(
            targets=["scatter_chart.data_frame.first_n", "box_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1, value=1),
        )
        model_manager["test_page"].controls.append(first_n_parameter)
        first_n_parameter.pre_build()

        # Add export_data action to relevant component
        model_manager["button"].actions = [export_data(id="test_action", targets=["scatter_chart", "box_chart"])]

        # Run action by picking the above added export_data action function and executing it with ()
        result = model_manager["test_action"].function(_controls=None)
        expected = {
            "download_dataframe_scatter_chart": {
                "filename": "scatter_chart.csv",
                "content": target_data_filter_and_parameter.to_csv(index=False),
                "type": None,
                "base64": False,
            },
            "download_dataframe_box_chart": {
                "filename": "box_chart.csv",
                "content": target_data_filter_and_parameter.to_csv(index=False),
                "type": None,
                "base64": False,
            },
        }

        assert result == expected


import dash
from asserts import assert_component_equal

import vizro.plotly.express as px
from vizro.models.types import capture
from vizro.actions import export_data, filter_interaction


@capture("action")
def custom_action_example():
    pass


# custom action with same name as some predefined action
def get_custom_action_with_known_name():
    @capture("action")
    def export_data():
        pass

    return export_data()


@pytest.fixture
def config_for_testing_all_components_with_actions(request, dash_data_table_with_id):
    """Instantiates managers with one page that contains four controls, two graphs and filter interaction."""
    # If the fixture is parametrised set the targets. Otherwise, set export_data without targets.
    export_data_action_function = (
        export_data(id="export_data_action", targets=request.param)
        if hasattr(request, "param")
        else export_data(id="export_data_action")
    )
    tab_1 = vm.Container(
        title="test_container_1",
        components=[
            vm.Graph(
                id="scatter_chart",
                figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                actions=[
                    vm.Action(function=filter_interaction(id="filter_interaction_action", targets=["scatter_chart_2"]))
                ],
            ),
            vm.Container(
                title="test_nested_container_1",
                components=[
                    vm.Graph(
                        id="scatter_chart_2",
                        figure=px.scatter(px.data.gapminder(), x="lifeExp", y="gdpPercap", custom_data=["continent"]),
                        actions=[vm.Action(id="custom_action", function=custom_action_example())],
                    ),
                ],
            ),
        ],
    )

    tab_2 = vm.Container(
        title="test_container_2",
        components=[
            vm.Table(
                id="vizro_table",
                figure=dash_data_table_with_id,
                actions=[
                    vm.Action(
                        function=filter_interaction(
                            id="table_filter_interaction_action", targets=["scatter_chart", "scatter_chart_2"]
                        ),
                    )
                ],
            ),
        ],
    )

    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Tabs(tabs=[tab_1, tab_2]),
            vm.Button(
                id="export_data_button",
                actions=[
                    vm.Action(function=export_data_action_function),
                    vm.Action(id="export_data_custom_action", function=get_custom_action_with_known_name()),
                ],
            ),
        ],
        controls=[
            vm.Filter(id="filter_continent", column="continent", selector=vm.Dropdown(id="filter_continent_selector")),
            vm.Filter(id="filter_country", column="country", selector=vm.Dropdown(id="filter_country_selector")),
            vm.Parameter(
                id="parameter_x",
                targets=["scatter_chart.x", "scatter_chart_2.x"],
                selector=vm.Dropdown(
                    id="parameter_x_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                    multi=False,
                    value="gdpPercap",
                ),
            ),
            vm.Parameter(
                id="parameter_y",
                targets=["scatter_chart.y", "scatter_chart_2.y"],
                selector=vm.Dropdown(
                    id="parameter_y_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                    multi=False,
                    value="lifeExp",
                ),
            ),
            vm.Parameter(
                id="vizro_table_row_selectable",
                targets=["vizro_table.row_selectable"],
                selector=vm.Dropdown(
                    id="parameter_table_row_selectable",
                    options=["multi", "single"],
                    multi=False,
                    value="single",
                ),
            ),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def export_data_outputs_expected(request):
    return {
        f"download_dataframe_{target}": dash.Output(
            {"action_id": "export_data_action", "target_id": target, "type": "download_dataframe"}, "data"
        )
        for target in request.param
    }


@pytest.fixture
def export_data_components_expected(request):
    return [
        dash.dcc.Download(id={"type": "download_dataframe", "action_id": "export_data_action", "target_id": target})
        for target in request.param
    ]


@pytest.mark.usefixtures("config_for_testing_all_components_with_actions")
class TestCallbackMapping:
    """Tests action callback mapping for predefined and custom actions."""

    @pytest.mark.parametrize(
        "export_data_outputs_expected", [("scatter_chart", "scatter_chart_2", "vizro_table")], indirect=True
    )
    def test_export_data_no_targets_set_mapping_outputs(self, export_data_outputs_expected):
        result = model_manager["export_data_action"]._transformed_outputs

        assert result == export_data_outputs_expected

    @pytest.mark.parametrize(
        "config_for_testing_all_components_with_actions, export_data_outputs_expected",
        [
            ([], ["scatter_chart", "scatter_chart_2", "vizro_table"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_targets_set_mapping_outputs(
        self, config_for_testing_all_components_with_actions, export_data_outputs_expected
    ):
        result = model_manager["export_data_action"]._transformed_outputs
        assert result == export_data_outputs_expected

    @pytest.mark.parametrize(
        "export_data_components_expected", [("scatter_chart", "scatter_chart_2", "vizro_table")], indirect=True
    )
    def test_export_data_no_targets_set_mapping_components(self, export_data_components_expected):
        result_components = model_manager["export_data_action"]._dash_components
        assert_component_equal(result_components, export_data_components_expected)

    @pytest.mark.parametrize(
        "config_for_testing_all_components_with_actions, export_data_components_expected",
        [
            ([], ["scatter_chart", "scatter_chart_2", "vizro_table"]),
            (["scatter_chart"], ["scatter_chart"]),
            (["scatter_chart", "scatter_chart_2"], ["scatter_chart", "scatter_chart_2"]),
        ],
        indirect=True,
    )
    def test_export_data_targets_set_mapping_components(
        self, config_for_testing_all_components_with_actions, export_data_components_expected
    ):
        result_components = model_manager["export_data_action"]._dash_components
        assert_component_equal(result_components, export_data_components_expected)
