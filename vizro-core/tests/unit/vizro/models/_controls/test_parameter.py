import pytest
import vizro.models as vm
from asserts import assert_component_equal
from vizro.managers import model_manager
from vizro.models._action._actions_chain import ActionsChain
from vizro.models._controls.parameter import Parameter
from vizro.models.types import CapturedCallable


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

    def test_check_target_present_failed(self):
        with pytest.raises(ValueError, match="Target scatter_chart_invalid not found in model_manager."):
            Parameter(targets=["scatter_chart_invalid.x"], selector=vm.Dropdown(options=["lifeExp", "pop"]))

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


@pytest.mark.usefixtures("managers_one_page_two_graphs")
class TestPreBuildMethod:
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

    @pytest.mark.parametrize("test_input", [vm.Slider(), vm.RangeSlider(), vm.DatePicker()])
    def test_numerical_and_temporal_selectors_missing_values(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{test_input.type} requires the arguments 'min' and 'max' when used within Parameter."
        ):
            parameter.pre_build()

    @pytest.mark.parametrize("test_input", [vm.Checklist(), vm.Dropdown(), vm.RadioItems()])
    def test_categorical_selectors_with_missing_options(self, test_input):
        parameter = Parameter(targets=["scatter_chart.x"], selector=test_input)
        page = model_manager["test_page"]
        page.controls = [parameter]
        with pytest.raises(
            TypeError, match=f"{parameter.selector.type} requires the argument 'options' when used within Parameter."
        ):
            parameter.pre_build()

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
        default_action = parameter.selector.actions[0]
        assert isinstance(default_action, ActionsChain)
        assert isinstance(default_action.actions[0].function, CapturedCallable)
        assert default_action.actions[0].id == f"parameter_action_{parameter.id}"


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
