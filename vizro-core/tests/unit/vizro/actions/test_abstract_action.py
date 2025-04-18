"""Unit tests for vizro.models.Action."""

from typing import Annotated, Literal

import pytest
from asserts import assert_component_equal
from dash import Output, State, html
from pydantic import Tag

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.models._action._actions_chain import ActionsChain


def annotate_action_type(cls):
    annotated_cls = Annotated[cls, Tag(cls.__name__)]
    vm.Graph.add_type("actions", annotated_cls)
    ActionsChain.add_type("actions", annotated_cls)

    return annotated_cls


@pytest.fixture
def class_action_with_no_args():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"

        def function(self):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_one_hardcoded_arg():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str

        def function(self):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_one_runtime_arg():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str

        def function(self, arg_1):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_one_runtime_arg_and_controls():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str

        def function(self, arg_1: str, _controls: dict):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_two_runtime_args():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str
        arg_2: str

        def function(self, arg_1: str, arg_2: str):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_one_runtime_and_one_hardcoded():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str
        arg_2: str

        def function(self, arg_1: str):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_mock_outputs(request):
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"

        def function(self):
            pass

        @property
        def outputs(self):
            return request.param

    return class_action


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
        assert action._action_name == "class_action"

    @pytest.mark.parametrize(
        "custom_action_fixture_name, runtime_inputs, expected_transformed_inputs",
        [
            ("class_action_with_no_args", {}, {}),
            (
                "class_action_with_one_runtime_arg",
                {"arg_1": "component.property"},
                {"arg_1": State("component", "property")},
            ),
            (
                "class_action_with_two_runtime_args",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1": State("component", "property"), "arg_2": State("component", "property")},
            ),
        ],
    )
    def test_runtime_inputs_valid(
        self, request, custom_action_fixture_name, runtime_inputs, expected_transformed_inputs
    ):
        custom_action = request.getfixturevalue(custom_action_fixture_name)
        action = custom_action(**runtime_inputs)

        assert action._transformed_inputs == expected_transformed_inputs

    # It's valid because arg_1 is a `hardcoded` parameter in the used class. So, it's not used as the runtime argument.
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

    # It's invalid because arg_1 is a `runtime` argument in the used class.
    @pytest.mark.parametrize(
        "hardcoded_input",
        [
            "",
            "component",
            "component_property",
            "component.property.property",
        ],
    )
    def test_hardcoded_inputs_invalid(self, class_action_with_one_runtime_arg, hardcoded_input):
        with pytest.raises(
            ValueError, match="Action inputs .* must be a string of the form <component_name>.<component_property>."
        ):
            # An error is raised when accessing _transformed_inputs which is fine because validation is then performed.
            class_action_with_one_runtime_arg(arg_1=hardcoded_input)._transformed_inputs()

    def test_builtin_arguments_with_empty_controls(self, class_action_with_one_runtime_arg_and_controls):
        action = class_action_with_one_runtime_arg_and_controls(arg_1="component.property")

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": {
                "filters": [],
                "parameters": [],
                "filter_interaction": [],
            },
        }

    def test_builtin_arguments_with_real_controls(
        self, class_action_with_one_runtime_arg_and_controls, page_actions_builtin_controls
    ):
        action = class_action_with_one_runtime_arg_and_controls(arg_1="component.property")

        assert action._transformed_inputs == {"arg_1": State("component", "property"), **page_actions_builtin_controls}

    # TODO: Adjust this test when _controls becomes a public field
    @pytest.mark.xfail(reason="Private fields can't be overwritten")
    def test_builtin_arguments_with_overwritten_controls(self, class_action_with_one_runtime_arg_and_controls):
        action = class_action_with_one_runtime_arg_and_controls(
            arg_1="component.property", _controls="component.property"
        )

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": State("component", "property"),
        }

    @pytest.mark.parametrize(
        "custom_action_fixture_name, runtime_inputs, expected_parameters, expected_runtime_args",
        [
            ("class_action_with_no_args", {}, set(), {}),
            ("class_action_with_one_hardcoded_arg", {"arg_1": "component.property"}, set(), {}),
            (
                "class_action_with_one_runtime_arg",
                {"arg_1": "component.property"},
                {"arg_1"},
                {"arg_1": "component.property"},
            ),
            (
                "class_action_with_two_runtime_args",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1", "arg_2"},
                {"arg_1": "component.property", "arg_2": "component.property"},
            ),
            (
                "class_action_with_one_runtime_arg_and_controls",
                {"arg_1": "component.property"},
                {"arg_1", "_controls"},
                {"arg_1": "component.property"},
            ),
            (
                "class_action_with_one_runtime_and_one_hardcoded",
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1"},
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

    @pytest.mark.parametrize(
        "class_action_with_mock_outputs, expected_transformed_outputs",
        [
            # List outputs
            ([], []),
            (["component.property"], Output("component", "property")),
            (
                ["component.property", "component.property"],
                [Output("component", "property"), Output("component", "property")],
            ),
            # Dict outputs
            ({}, {}),
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
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            class_action_with_mock_outputs()._transformed_outputs()


class TestAbstractActionBuild:
    def test_custom_action_build(self, class_action_with_no_args):
        action_id = "action_test"
        action = class_action_with_no_args(id=action_id)

        assert_component_equal(
            action.build(), html.Div(id=f"{action_id}_action_model_components_div", children=[], hidden=True)
        )
