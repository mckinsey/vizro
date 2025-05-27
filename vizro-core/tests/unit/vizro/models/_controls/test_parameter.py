import pytest
from asserts import assert_component_equal

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import data_manager, model_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls.parameter import Parameter


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestParameterInstantiation:
    def test_instantiation(self):
        parameter = Parameter(
            targets=["scatter_chart.x"],
            selector=vm.Dropdown(
                options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp", title="Choose x-axis"
            ),
        )
        assert parameter.type == "parameter"
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.type == "dropdown"

    def test_check_dot_notation_failed(self):
        with pytest.raises(
            ValueError,
            match="Invalid target scatter_chart. "
            "Targets must be supplied in the form <target_component>.<target_argument>",
        ):
            Parameter(targets=["scatter_chart"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    @pytest.mark.parametrize("target", ["scatter_chart.data_frame", "scatter_chart.data_frame.argument.nested_arg"])
    def test_check_data_frame_as_target_argument_failed(self, target):
        with pytest.raises(
            ValueError,
            match=f"Invalid target {target}. 'data_frame' target must be supplied in the form "
            f"<target_component>.data_frame.<dynamic_data_argument>",
        ):
            Parameter(targets=[target], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    def test_duplicate_parameter_target_failed(self):
        with pytest.raises(ValueError, match="Duplicate parameter targets {'scatter_chart.x'} found."):
            Parameter(targets=["scatter_chart.x", "scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

    def test_duplicate_parameter_target_failed_two_params(self):
        with pytest.raises(ValueError, match="Duplicate parameter targets {'scatter_chart.x'} found."):
            Parameter(targets=["scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
            Parameter(targets=["scatter_chart.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))


class TestPreBuildMethod:
    def test_filter_not_in_page(self):
        with pytest.raises(ValueError, match="Control parameter_id should be defined within a Page object"):
            Parameter(
                id="parameter_id",
                targets=["scatter_chart.x"],
                selector=vm.Dropdown(options=["lifeExp", "pop"]),
            ).pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input, title",
        [
            (vm.Checklist(options=["lifeExp", "gdpPercap", "pop"], value=["lifeExp"]), "x"),
            (vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp"), "x"),
            (
                vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], value="lifeExp", title="Choose x-axis"),
                "Choose x-axis",
            ),
        ],
    )
    def test_set_target_and_title_valid(self, test_input, title):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()
        assert parameter.targets == ["scatter_chart.x"]
        assert parameter.selector.title == title

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    def test_targets_present_invalid(self):
        parameter = Parameter(targets=["scatter_chart_invalid.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))
        model_manager["test_page"].controls = [parameter]
        with pytest.raises(ValueError, match="Target scatter_chart_invalid not found within the test_page."):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider(), vm.DatePicker()])
    def test_numerical_and_temporal_selectors_missing_values(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{test_input.type} requires the arguments 'min' and 'max' when used within Parameter."
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize("test_input", [vm.Checklist(), vm.Dropdown(), vm.RadioItems()])
    def test_categorical_selectors_with_missing_options(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{parameter.selector.type} requires the argument 'options' when used within Parameter."
        ):
            parameter.pre_build()

    @pytest.mark.usefixtures("managers_one_page_two_graphs")
    @pytest.mark.parametrize(
        "test_input",
        [
            (vm.Checklist(options=["lifeExp", "gdpPercap", "pop"], value=["lifeExp"])),
            (vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"], multi=False, value="lifeExp")),
            (vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"], value="lifeExp")),
        ],
    )
    def test_set_actions(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()

        default_actions_chain = parameter.selector.actions[0]
        default_action = default_actions_chain.actions[0]

        assert isinstance(default_actions_chain, ActionsChain)
        assert isinstance(default_action, _AbstractAction)
        assert default_action.id == f"__parameter_action_{parameter.id}"

    def test_set_custom_action(self, managers_one_page_two_graphs, identity_action_function):
        action_function = identity_action_function()
        parameter = vm.Parameter(
            targets=["scatter_chart.x"],
            selector=vm.RadioItems(
                options=["lifeExp", "gdpPercap", "pop"],
                actions=[vm.Action(function=action_function)],
            ),
        )
        model_manager["test_page"].controls = [parameter]
        parameter.pre_build()

        default_actions_chain = parameter.selector.actions[0]
        default_action = default_actions_chain.actions[0]

        assert isinstance(default_actions_chain, ActionsChain)
        assert default_action.function is action_function

    @pytest.mark.usefixtures("managers_one_page_two_graphs_with_dynamic_data")
    @pytest.mark.parametrize(
        "filter_targets, expected_parameter_targets",
        [
            ([], {"scatter_chart.data_frame.first_n"}),
            (["scatter_chart"], {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart"}),
            (
                ["scatter_chart", "box_chart"],
                {"scatter_chart.data_frame.first_n", "filter_id", "scatter_chart", "box_chart"},
            ),
        ],
    )
    def test_targets_argument_for_data_frame_parameter_action(
        self, filter_targets, expected_parameter_targets, gapminder_dynamic_first_n_last_n_function
    ):
        data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function

        if filter_targets:
            dynamic_filter = vm.Filter(id="filter_id", column="pop", targets=filter_targets)
            model_manager["test_page"].controls.append(dynamic_filter)
            dynamic_filter.pre_build()

        data_frame_parameter = vm.Parameter(
            id="test_data_frame_parameter",
            targets=["scatter_chart.data_frame.first_n"],
            selector=vm.Slider(id="first_n_parameter", min=1, max=10, step=1),
        )
        model_manager["test_page"].controls.append(data_frame_parameter)
        data_frame_parameter.pre_build()

        default_action = data_frame_parameter.selector.actions[0].actions[0]
        assert set(default_action.targets) == expected_parameter_targets

    @pytest.mark.usefixtures("managers_one_page_container_controls")
    def test_set_container_parameter_default(self):
        parameter = model_manager["container_parameter"]
        parameter.pre_build()

        assert parameter.selector.extra == {"inline": True}


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestParameterBuild:
    """Tests parameter build method."""

    @pytest.mark.parametrize(
        "test_input",
        [
            vm.Checklist(options=["lifeExp", "gdpPercap", "pop"]),
            vm.Dropdown(options=["lifeExp", "gdpPercap", "pop"]),
            vm.RadioItems(options=["lifeExp", "gdpPercap", "pop"]),
        ],
    )
    def test_build_parameter(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        parameter.pre_build()
        result = parameter.build()
        expected = test_input.build()

        assert_component_equal(result, expected)
