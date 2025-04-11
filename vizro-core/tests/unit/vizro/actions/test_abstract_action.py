"""Unit tests for vizro.models.Action."""

from typing import Annotated, Literal

import pytest
from asserts import assert_component_equal
from dash import Output, State, html
from pydantic import Tag

import vizro.models as vm
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.actions._abstract_action import _AbstractAction
from vizro.models._action._actions_chain import ActionsChain

# TODO-QQ: Check test_builtin_arguments_with_overwritten_controls: this test fails because model fields can't be private
#  Test is set as: @pytest.mark.xfail()
#  This doesn't allow users to overwrite any private parameter like: _controls
#  If _controls: str set as a model field, I get:
# E       pydantic_core._pydantic_core.ValidationError: 1 validation error for class_action_with_one_arg_and_controls
# E       _controls
# E         Extra inputs are not permitted [type=extra_forbidden, input_value='component.property', input_type=str]

# TODO: Optimise fixtures
# TODO: Find suffice naming for fixtures and hardcoded vs runtime vs model_files vs arg vs param.


@pytest.fixture
def class_action_with_no_args():
    class class_action_with_no_args(_AbstractAction):
        type: Literal["class_action_with_no_args"] = "class_action_with_no_args"

        def function(self):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_no_args = Annotated[class_action_with_no_args, Tag("class_action_with_no_args")]
    vm.Graph.add_type("actions", class_action_with_no_args)
    ActionsChain.add_type("actions", class_action_with_no_args)

    return class_action_with_no_args


@pytest.fixture
def class_action_with_one_hardcoded_arg():
    class class_action_with_one_hardcoded_arg(_AbstractAction):
        type: Literal["class_action_with_one_hardcoded_arg"] = "class_action_with_one_hardcoded_arg"
        arg_1: str

        def function(self):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_one_hardcoded_arg = Annotated[
        class_action_with_one_hardcoded_arg, Tag("class_action_with_one_hardcoded_arg")
    ]
    vm.Graph.add_type("actions", class_action_with_one_hardcoded_arg)
    ActionsChain.add_type("actions", class_action_with_one_hardcoded_arg)

    return class_action_with_one_hardcoded_arg


@pytest.fixture
def class_action_with_one_arg():
    class class_action_with_one_arg(_AbstractAction):
        type: Literal["class_action_with_one_arg"] = "class_action_with_one_arg"
        arg_1: str

        def function(self, arg_1):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_one_arg = Annotated[class_action_with_one_arg, Tag("class_action_with_one_arg")]
    vm.Graph.add_type("actions", class_action_with_one_arg)
    ActionsChain.add_type("actions", class_action_with_one_arg)

    return class_action_with_one_arg


@pytest.fixture
def class_action_with_one_arg_and_controls():
    class class_action_with_one_arg_and_controls(_AbstractAction):
        type: Literal["class_action_with_one_arg_and_controls"] = "class_action_with_one_arg_and_controls"
        arg_1: str

        def function(self, arg_1: str, _controls: dict):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_one_arg_and_controls = Annotated[
        class_action_with_one_arg_and_controls, Tag("class_action_with_one_arg_and_controls")
    ]
    vm.Graph.add_type("actions", class_action_with_one_arg_and_controls)
    ActionsChain.add_type("actions", class_action_with_one_arg_and_controls)

    return class_action_with_one_arg_and_controls


@pytest.fixture
def class_action_with_two_args():
    class class_action_with_two_args(_AbstractAction):
        type: Literal["class_action_with_two_args"] = "class_action_with_two_args"
        arg_1: str
        arg_2: str

        def function(self, arg_1: str, arg_2: str):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_two_args = Annotated[class_action_with_two_args, Tag("class_action_with_two_args")]
    vm.Graph.add_type("actions", class_action_with_two_args)
    ActionsChain.add_type("actions", class_action_with_two_args)

    return class_action_with_two_args


@pytest.fixture
def class_action_with_one_runtime_and_one_parameter():
    class class_action_with_one_runtime_and_one_parameter(_AbstractAction):
        type: Literal["class_action_with_one_runtime_and_one_parameter"] = (
            "class_action_with_one_runtime_and_one_parameter"
        )
        arg_1: str
        arg_2: str

        def function(self, arg_1: str, _controls: dict):
            pass

        @property
        def outputs(self):
            return []

    class_action_with_one_runtime_and_one_parameter = Annotated[
        class_action_with_one_runtime_and_one_parameter, Tag("class_action_with_one_runtime_and_one_parameter")
    ]
    vm.Graph.add_type("actions", class_action_with_one_runtime_and_one_parameter)
    ActionsChain.add_type("actions", class_action_with_one_runtime_and_one_parameter)

    return class_action_with_one_runtime_and_one_parameter


@pytest.fixture
def class_action_with_mock_outputs(request):
    class class_action_with_mock_outputs(_AbstractAction):
        type: Literal["class_action_with_mock_outputs"] = "class_action_with_mock_outputs"

        def function(self):
            pass

        @property
        def outputs(self):
            return request.param

    class_action_with_mock_outputs = Annotated[class_action_with_mock_outputs, Tag("class_action_with_mock_outputs")]
    vm.Graph.add_type("actions", class_action_with_mock_outputs)
    ActionsChain.add_type("actions", class_action_with_mock_outputs)

    return class_action_with_mock_outputs


@pytest.fixture
def _real_builtin_controls(standard_px_chart):
    """Instantiates managers with one page that contains filter, parameter, and filter_interaction actions."""
    vm.Page(
        title="title",
        components=[
            vm.Graph(
                id="graph_1",
                figure=standard_px_chart,
                actions=[filter_interaction(id="graph_filter_interaction", targets=["graph_2"])],
            ),
            vm.Graph(id="graph_2", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(id="filter", column="continent", selector=vm.Dropdown(id="filter_selector")),
            vm.Parameter(
                id="parameter",
                targets=["graph_1.x"],
                selector=vm.Checklist(
                    id="parameter_selector",
                    options=["lifeExp", "gdpPercap", "pop"],
                ),
            ),
        ],
    )

    Vizro._pre_build()

    return {
        "_controls": {
            "filters": [
                State("filter_selector", "value"),
            ],
            "parameters": [
                State("parameter_selector", "value"),
            ],
            "filter_interaction": [
                {"clickData": State("graph_1", "clickData"), "modelID": State("graph_1", "id")},
            ],
        }
    }


class TestAbstractActionInstantiation:
    """Tests _AbstractAction instantiation."""

    def test_action_mandatory_only(self, class_action_with_no_args):
        action = class_action_with_no_args()

        assert hasattr(action, "id")
        assert hasattr(action, "function")
        assert action.outputs == []

        assert not action._legacy
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._dash_components == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "class_action_with_no_args"

    @pytest.mark.parametrize(
        "custom_action_fixture_name, runtime_inputs, expected_transformed_inputs",
        [
            ("class_action_with_no_args", {}, {}),
            ("class_action_with_one_arg", {"arg_1": "component.property"}, {"arg_1": State("component", "property")}),
            (
                "class_action_with_two_args",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1": State("component", "property"), "arg_2": State("component", "property")},
            ),
        ],
    )
    def test_runtime_inputs(self, request, custom_action_fixture_name, runtime_inputs, expected_transformed_inputs):
        custom_action = request.getfixturevalue(custom_action_fixture_name)
        action = custom_action(**runtime_inputs)

        assert action._transformed_inputs == expected_transformed_inputs

    # It's valid because arg_1 is hardcoded input in the used class - it's not used as the runtime input.
    @pytest.mark.parametrize(
        "hardcoded_input",
        [
            "",
            "component",
            "component_property",
            "component.property.property",
        ],
    )
    def test_hardcoded_inputs_valid(self, class_action_with_one_hardcoded_arg, hardcoded_input):
        action = class_action_with_one_hardcoded_arg(arg_1=hardcoded_input)

        assert action._transformed_inputs == {}

    # It's invalid because arg_1 is runtime input in the used class
    @pytest.mark.parametrize(
        "hardcoded_input",
        [
            "",
            "component",
            "component_property",
            "component.property.property",
        ],
    )
    def test_hardcoded_inputs_invalid(self, class_action_with_one_arg, hardcoded_input):
        with pytest.raises(
            ValueError, match="Action inputs .* must be a string of the form <component_name>.<component_property>."
        ):
            # Error is raised when _transformed_outputs is accessed which is okay as the output is the class method.
            class_action_with_one_arg(arg_1=hardcoded_input)._transformed_inputs()

    @pytest.mark.parametrize(
        "custom_action_fixture_name, runtime_inputs, expected_parameters, expected_runtime_args",
        [
            ("class_action_with_no_args", {}, set(), {}),
            ("class_action_with_one_arg", {"arg_1": "component.property"}, {"arg_1"}, {"arg_1": "component.property"}),
            (
                "class_action_with_two_args",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1", "arg_2"},
                {"arg_1": "component.property", "arg_2": "component.property"},
            ),
            (
                "class_action_with_one_arg_and_controls",
                {"arg_1": "component.property"},
                {"arg_1", "_controls"},
                {
                    "arg_1": "component.property",
                },
            ),
            (
                "class_action_with_one_runtime_and_one_parameter",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1", "_controls"},
                {"arg_1": "component.property"},
            ),
        ],
    )
    def test_parameters_and_runtime_args(
        self, request, custom_action_fixture_name, runtime_inputs, expected_parameters, expected_runtime_args
    ):
        custom_action = request.getfixturevalue(custom_action_fixture_name)
        action = custom_action(**runtime_inputs)

        assert action._parameters == expected_parameters
        assert action._runtime_args == expected_runtime_args

    def test_builtin_arguments_with_empty_controls(self, class_action_with_one_arg_and_controls):
        action = class_action_with_one_arg_and_controls(arg_1="component.property")

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": {
                "filters": [],
                "parameters": [],
                "filter_interaction": [],
            },
        }

    def test_builtin_arguments_with_real_controls(self, class_action_with_one_arg_and_controls, _real_builtin_controls):
        action = class_action_with_one_arg_and_controls(arg_1="component.property")

        assert action._transformed_inputs == {"arg_1": State("component", "property"), **_real_builtin_controls}

    @pytest.mark.xfail()
    def test_builtin_arguments_with_overwritten_controls(self, class_action_with_one_arg_and_controls):
        action = class_action_with_one_arg_and_controls(arg_1="component.property", _controls="component.property")

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": State("component", "property"),
        }

    @pytest.mark.parametrize(
        "class_action_with_mock_outputs, expected_transformed_outputs",
        [
            ([], []),
            (["component.property"], Output("component", "property")),
            (
                ["component.property", "component.property"],
                [Output("component", "property"), Output("component", "property")],
            ),
            (
                {"output_1": "component.property"},
                {"output_1": Output("component", "property")},
            ),
            (
                {"output_1": "component.property", "output_2": "component.property"},
                {"output_1": Output("component", "property"), "output_2": Output("component", "property")},
            ),
        ],
        indirect=["class_action_with_mock_outputs"],
    )
    def test_outputs_valid(self, class_action_with_mock_outputs, expected_transformed_outputs):
        action = class_action_with_mock_outputs()

        assert action._transformed_outputs == expected_transformed_outputs

    @pytest.mark.parametrize(
        "class_action_with_mock_outputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
            {"output_1": ""},
            {"output_1": "component.property", "output_2": ""},
        ],
        indirect=["class_action_with_mock_outputs"],
    )
    def test_outputs_invalid(self, class_action_with_mock_outputs):
        with pytest.raises(
            ValueError, match="Action outputs .* must be a string of the form <component_name>.<component_property>."
        ):
            # Error is raised when _transformed_outputs is accessed which is okay as the output is the class method.
            class_action_with_mock_outputs()._transformed_outputs()


class TestAbstractActionBuild:
    def test_custom_action_build(self, class_action_with_no_args):
        action_id = "action_test"
        action = class_action_with_no_args(id=action_id)

        assert_component_equal(
            action.build(), html.Div(id=f"{action_id}_action_model_components_div", children=[], hidden=True)
        )
