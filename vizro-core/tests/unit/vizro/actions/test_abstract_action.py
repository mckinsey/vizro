from typing import Annotated, Literal

import pytest
from asserts import assert_component_equal
from dash import Output, State, html
from pydantic import Tag

import vizro.models as vm
from vizro.actions._abstract_action import _AbstractAction
from vizro.models._action._actions_chain import ActionsChain


# TODO AM: check this
def annotate_action_type(cls):
    # annotated_cls = Annotated[cls, Tag(cls.__name__)]
    # vm.Graph.add_type("actions", annotated_cls)
    # ActionsChain.add_type("actions", annotated_cls)

    return cls


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
def class_action_with_one_static_arg():
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
def class_action_with_two_static_args():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        arg_1: str
        arg_2: str

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
def class_action_with_one_runtime_and_one_static():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"
        runtime_arg: str
        static_arg: str

        def function(self, runtime_arg: str):
            pass

        @property
        def outputs(self):
            return []

    return class_action


@pytest.fixture
def class_action_with_builtin_runtime_arg():
    @annotate_action_type
    class class_action(_AbstractAction):
        type: Literal["class_action"] = "class_action"

        def function(self, _controls: dict):
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


class TestAbstractActionInputs:
    @pytest.mark.parametrize(
        "custom_action_fixture_name, inputs, expected_transformed_inputs",
        [
            ("class_action_with_no_args", {}, {}),
            (
                "class_action_with_one_static_arg",
                {"arg_1": "anything"},
                {},
            ),
            (
                "class_action_with_two_static_args",
                {"arg_1": "anything", "arg_2": "anything"},
                {},
            ),
            (
                "class_action_with_one_runtime_arg",
                {"arg_1": "component.property"},
                {"arg_1": State("component", "property")},
            ),
            (
                "class_action_with_two_runtime_args",
                {"arg_1": "component_1.property_1", "arg_2": "component_2.property_2"},
                {"arg_1": State("component_1", "property_1"), "arg_2": State("component_2", "property_2")},
            ),
            (
                "class_action_with_one_runtime_and_one_static",
                {"runtime_arg": "component_1.property_1", "static_arg": "anything"},
                {"runtime_arg": State("component_1", "property_1")},
            ),
            (
                "class_action_with_builtin_runtime_arg",
                {},
                {
                    "_controls": {
                        "filters": [],
                        "parameters": [],
                        "filter_interaction": [],
                    }
                },
            ),
        ],
    )
    def test_inputs_valid(self, request, custom_action_fixture_name, inputs, expected_transformed_inputs):
        custom_action = request.getfixturevalue(custom_action_fixture_name)
        action = custom_action(**inputs)

        assert action._transformed_inputs == expected_transformed_inputs

    @pytest.mark.parametrize(
        "input",
        [
            "",
            "component",
            "component_property",
            "component.property.property",
        ],
    )
    def test_runtime_inputs_invalid(self, class_action_with_one_runtime_arg, input):
        with pytest.raises(
            ValueError, match="Action inputs .* must be a string of the form <component_name>.<component_property>."
        ):
            # An error is raised when accessing _transformed_inputs which is fine because validation is then performed.
            class_action_with_one_runtime_arg(arg_1=input)._transformed_inputs

    # TODO: Adjust this test when _controls becomes a public field. Should demonstrate that a runtime arg called
    # controls overrides the inbuilt behaviour. This could be done as a new test case in TestAbstractActionInputs.
    @pytest.mark.xfail(reason="Private fields can't be overwritten")
    def test_builtin_runtime_arg_with_overwritten_controls(self, class_action_with_builtin_runtime_arg):
        action = class_action_with_builtin_runtime_arg()

        assert action._transformed_inputs == {"_controls": State("component", "property")}


class TestBuiltinRuntimeArgs:
    """Test the actual values of the runtime args are correct in a real scenario."""

    def test_builtin_runtime_arg_controls(self, class_action_with_builtin_runtime_arg, page_actions_builtin_controls):
        action = class_action_with_builtin_runtime_arg()

        assert action._transformed_inputs == page_actions_builtin_controls


class TestAbstractActionOutputs:
    @pytest.mark.parametrize(
        "class_action_with_mock_outputs, expected_transformed_outputs",
        [
            # List outputs
            ([], []),
            (["component.property"], Output("component", "property")),
            (
                ["component_1.property_1", "component_2.property_2"],
                [Output("component_1", "property_1"), Output("component_2", "property_2")],
            ),
            # Dict outputs
            ({}, {}),
            (
                {"output_1": "component.property"},
                {"output_1": Output("component", "property")},
            ),
            (
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": Output("component_1", "property_1"), "output_2": Output("component_2", "property_2")},
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
            class_action_with_mock_outputs()._transformed_outputs


class TestAbstractActionBuild:
    def test_abstract_action_build(self, class_action_with_no_args):
        action = class_action_with_no_args(id="action_test")

        assert_component_equal(
            action.build(), html.Div(id="action_test_action_model_components_div", children=[], hidden=True)
        )
