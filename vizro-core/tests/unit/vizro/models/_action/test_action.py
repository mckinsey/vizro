"""Unit tests for vizro.models.Action."""
import random

import dash
from dash._callback_context import context_value
from dash._utils import AttributeDict

import pytest
from vizro import Vizro
from vizro.models._action._action import Action
from vizro.models.types import capture
from vizro.actions._actions_utils import (
    CallbackTriggerDict,
)

# TODO: REMOVE IT
@pytest.fixture
def expected_function_return_value(request):
    return request.param


@pytest.fixture
def custom_action_function(request):
    @capture("action")
    def fun():
        return request.param
    return fun

@pytest.fixture
@capture("action")
def test_action_function():
    pass

@pytest.fixture
def callback_context_outputs_grouping(request):
    """Mock dash.callback_context that represents outputs grouping  Filter value selection."""
    outputs = request.param

    outputs_grouping = {output: None for output in outputs}
    outputs_grouping.update({"action_finished": None})
    mock_callback_context = {
        "outputs_grouping": outputs_grouping
    }
    context_value.set(AttributeDict(**mock_callback_context))
    return context_value


class TestActionInstantiation:
    """Tests model instantiation."""

    def test_create_action_mandatory_only(self, test_action_function):
        action = Action(function=test_action_function)

        assert hasattr(action, "id")
        assert action.function == test_action_function
        assert action.inputs == []
        assert action.outputs == []

    def test_create_action_mandatory_and_optional(self, test_action_function):
        inputs = ["component_1.property_A", "component_1.property_B"]
        outputs = ["component_2.property_A", "component_2.property_B"]

        action = Action(
            function=test_action_function,
            inputs=inputs,
            outputs=outputs
        )

        assert hasattr(action, "id")
        assert action.function == test_action_function
        assert action.inputs == inputs
        assert action.outputs == outputs

    @pytest.mark.parametrize(
        "inputs, outputs",
        [
            ([], []),
            (["component.property"], ["component.property"]),
            (["component.property", "component.property"], ["component.property", "component.property"]),
            (["Component_1.Property_A", "Component_2.Property_B"], ["Component_1.Property_A", "Component_2.Property_B"]),
        ],
    )
    def test_inputs_outputs_valid(self, inputs, outputs, test_action_function):
        action = Action(
            function=test_action_function,
            inputs=inputs,
            outputs=outputs
        )

        assert action.inputs == inputs
        assert action.outputs == outputs

    @pytest.mark.parametrize(
        "inputs",
        [
            None,
            "string",
            "component_property",
            "compo-nent.property",
            "component.property_1",
        ],
    )
    def test_inputs_invalid(self, inputs, test_action_function):
        with pytest.raises(Exception):
            Action(function=test_action_function, inputs=inputs, outputs=[])

    @pytest.mark.parametrize(
        "outputs",
        [
            None,
            "string",
            "component_property",
            "compo-nent.property",
            "component.property_1",
        ],
    )
    def test_inputs_invalid(self, outputs, test_action_function):
        with pytest.raises(Exception):
            Action(function=test_action_function, inputs=[], outputs=outputs)

class TestActionBuild:
    """Tests action build method."""
    def test_build_no_returned_components_for_custom_action(self, test_action_function):
        action = Action(function=test_action_function)
        result = action.build()
        expected = list()
        assert result == expected

"""
class TestActionPrivateMethods:
1. _get_callback_mapping - no inputs, no outputs
2. _get_callback_mapping - inputs and outputs - parametrization with one input one output, multi inputs multi outputs and so on
3. _action_callback_function - function without inputs and with no return value (no outputs)
5. _action_callback_function - function with inputs and with dictionary return value 
6. _action_callback_function - function with inputs with single element return value 
7. _action_callback_function - function with inputs with list of return values  
"""

class TestActionPrivateMethods:
    """Test action private methods."""
    def test_get_callback_mapping_no_inputs_no_outputs(self, test_action_function):
        action = Action(id="action_test", function=test_action_function)
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == {'trigger': dash.Input({"action_name": "action_test", "type": "action_trigger"}, "data")}
        assert callback_outputs == {'action_finished': dash.Output("action_finished", "data")}
        assert action_components == list()

    @pytest.mark.parametrize(
        "inputs, outputs",
        [
            (["component_1.property"], ["component_1.property"]),
            (["component_1.property", "component_2.property"], ["component_1.property", "component_2.property"]),
        ],
    )
    def test_get_callback_mapping_with_inputs_and_outputs(self, inputs, outputs, test_action_function):
        action = Action(
            function=test_action_function,
            inputs=inputs,
            outputs=outputs,
        )
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == {
            **{
                f'{input.split(".")[0]}_{input.split(".")[1]}': dash.State(input.split(".")[0], input.split(".")[1])
                for input in inputs
            },
            'trigger': dash.Input({"action_name": action.id, "type": "action_trigger"}, "data")
        }
        assert callback_outputs == {
            **{
                f'{output.split(".")[0]}_{output.split(".")[1]}': dash.Output(
                    output.split(".")[0], output.split(".")[1], allow_duplicate=True
                )
                for output in outputs
            },
            'action_finished': dash.Output("action_finished", "data")
        }
        assert action_components == list()

    @pytest.mark.parametrize(
        "custom_action_function, callback_context_outputs_grouping, expected_function_return_value",
        [
            (None, [], {'action_finished': None}),
            ({'component_1_property': 'new_value'}, ['component_1_property'], {'action_finished': None, 'component_1_property': 'new_value'}),
            ('new_value', ['component_1_property'], {'action_finished': None, 'component_1_property': 'new_value'}),
            (['new_value', 'new_value_2'], ['component_1_property', 'component_2_property'], {'action_finished': None, 'component_1_property': 'new_value', 'component_2_property': 'new_value_2'}),
        ],
        indirect=True,
    )
    def test_action_callback_function_return_value_valid(self, custom_action_function, callback_context_outputs_grouping, expected_function_return_value):
        action = Action(function=custom_action_function())
        result = action._action_callback_function()
        assert result == expected_function_return_value

    @pytest.mark.parametrize(
        "custom_action_function, callback_context_outputs_grouping",
        [
            (None, ['component_1_property']),
            ("new_value", []),
            ("new_value", ['component_1_property', 'component_2_property']),
            (["new_value"], []),
            (["new_value"], ['component_1_property', 'component_2_property']),
            (["new_value", "new_value_2"], ['component_1_property']),
            ({'component_1_property': 'new_value'}, []),
            ({'component_1_property': 'new_value'}, ['component_1_property', 'component_2_property']),
            ({'component_1_property': 'new_value', 'component_2_property': 'new_value_2'}, ['component_1_property']),
        ],
        indirect=True,
    )
    def test_action_callback_function_return_value_invalid(self, custom_action_function, callback_context_outputs_grouping):
        action = Action(function=custom_action_function())
        with pytest.raises(ValueError):
            action._action_callback_function()
