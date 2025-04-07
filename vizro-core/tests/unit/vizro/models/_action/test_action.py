"""Unit tests for vizro.models.Action."""

import textwrap

import pytest
from asserts import assert_component_equal
from dash import Output, State, html
from pydantic import ValidationError

import vizro.models as vm
from vizro import Vizro
from vizro.actions import filter_interaction
from vizro.models._action._action import Action
from vizro.models.types import capture


@pytest.fixture
def custom_action_mock_return(request):
    """Return an action function that returns the value of the request param."""

    @capture("action")
    def _custom_action_mock_return():
        return request.param

    return _custom_action_mock_return


@pytest.fixture
def custom_action_with_parameters(request):
    """Return a custom action function with the specified parameters."""
    # Parameters in format: "arg_1, arg_2, arg_3"
    parameters = ", ".join(request.param)

    # Create a function with the specified number of parameters that returns their values
    func_code = textwrap.dedent(f"""
        from vizro.models.types import capture

        @capture("action")
        def custom_action({parameters}):
            pass
    """)

    local_vars = {}
    exec(func_code, {}, local_vars)

    return local_vars["custom_action"]


# TODO: This is used in the single test only. Should it be moved there?
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


class TestActionInstantiation:
    """Tests model instantiation."""

    def test_action_mandatory_only(self, identity_action_function):
        function = identity_action_function()
        action = Action(function=function)

        assert hasattr(action, "id")
        assert action.function is function
        assert action.inputs == []
        assert action.outputs == []

        # TODO: Should we test private attributes?
        assert action._legacy is False
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._dash_components == []
        assert action._action_name == "_identity_action_function"

    @pytest.mark.parametrize(
        "inputs, _transformed_inputs",
        [
            ([], []),
            (["component.property"], [State("component", "property")]),
            (
                ["component.property", "component.property"],
                [State("component", "property"), State("component", "property")],
            ),
        ],
    )
    def test_model_field_inputs_valid(self, identity_action_function, inputs, _transformed_inputs):
        action = Action(function=identity_action_function(), inputs=inputs)

        assert action._legacy is True
        assert action.inputs == inputs
        assert action._transformed_inputs == _transformed_inputs

    @pytest.mark.parametrize(
        "inputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_model_filed_inputs_invalid(self, inputs, identity_action_function):
        with pytest.raises(ValidationError, match="String should match pattern"):
            Action(function=identity_action_function(), inputs=inputs)

    @pytest.mark.parametrize(
        "inputs",
        [
            [None],
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_runtime_hardcoded_inputs(self, inputs, identity_action_function):
        action = Action(function=identity_action_function(*inputs))

        assert action._legacy is True
        assert action.inputs == []
        assert action._transformed_inputs == []

    @pytest.mark.parametrize(
        "custom_action_with_parameters, inputs, _transformed_inputs",
        [
            ([], [], {}),
            (["arg_1"], ["component.property"], {"arg_1": State("component", "property")}),
            (
                ["arg_1", "arg_2"],
                ["component.property", "component.property"],
                {"arg_1": State("component", "property"), "arg_2": State("component", "property")},
            ),
        ],
        indirect=["custom_action_with_parameters"],
    )
    def test_runtime_id_property_inputs(self, custom_action_with_parameters, inputs, _transformed_inputs):
        action = Action(function=custom_action_with_parameters(*inputs))

        assert action._legacy is False
        assert action.inputs == []
        assert action._transformed_inputs == _transformed_inputs

    # TODO: Add more tests here and reorder the tests to be more logical.
    # TODO: Should the "_legacy" testing be removed?
    # TODO: Should we test both runtime arguments as list and dict?
    @pytest.mark.parametrize(
        "custom_action_with_parameters, runtime_inputs, model_field_inputs, expected_legacy, _transformed_inputs",
        [
            ([], {}, [], False, {}),
            (["arg_1"], {}, ["component.property"], True, [State("component", "property")]),
            (["arg_1"], {"arg_1": "test"}, [], True, []),
            (["arg_1", "arg_2"], {"arg_1": "test"}, ["component.property"], True, [State("component", "property")]),
            (["arg_1"], {"arg_1": "component.property"}, [], False, {"arg_1": State("component", "property")}),
            (
                ["arg_1", "arg_2"],
                {"arg_1": "component.property"},
                ["component.property"],
                True,
                [State("component", "property")],
            ),
        ],
        indirect=["custom_action_with_parameters"],
    )
    def test_mixed_runtime_and_model_field_inputs(
        self,
        custom_action_with_parameters,
        runtime_inputs,
        model_field_inputs,
        expected_legacy,
        _transformed_inputs,
    ):
        # Conditionally set model field inputs only if not empty so we don't stick with legacy actions only.
        if model_field_inputs:
            # Action is legacy because it has model field inputs
            action = Action(function=custom_action_with_parameters(**runtime_inputs), inputs=model_field_inputs)
        else:
            # Action is not legacy if all runtime inputs are in id.property format. Otherwise it is legacy.
            action = Action(function=custom_action_with_parameters(**runtime_inputs))

        assert action._legacy is expected_legacy
        assert action.inputs == model_field_inputs
        assert action._transformed_inputs == _transformed_inputs

    @pytest.mark.parametrize("custom_action_with_parameters", [(["arg_1, _controls"])], indirect=True)
    def test_builtin_argument_with_empty_controls(self, custom_action_with_parameters):
        action = Action(function=custom_action_with_parameters("component.property"))

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": {
                "filters": [],
                "parameters": [],
                "filter_interaction": [],
            },
        }

    @pytest.mark.parametrize("custom_action_with_parameters", [(["arg_1, _controls"])], indirect=True)
    def test_builtin_argument_with_real_controls(
        self,
        custom_action_with_parameters,
        _real_builtin_controls,
    ):
        action = Action(function=custom_action_with_parameters("component.property"))

        assert action._transformed_inputs == {"arg_1": State("component", "property"), **_real_builtin_controls}

    @pytest.mark.parametrize("custom_action_with_parameters", [(["arg_1, _controls"])], indirect=True)
    def test_builtin_argument_with_overwritten_controls(
        self,
        custom_action_with_parameters,
    ):
        action = Action(function=custom_action_with_parameters("component.property", "component.property"))

        assert action._transformed_inputs == {
            "arg_1": State("component", "property"),
            "_controls": State("component", "property"),
        }

    # The "runtime_inputs" is added here to test outputs for both legacy and non-legacy actions
    @pytest.mark.parametrize("runtime_inputs", [[], ["hardcoded_input"]])
    @pytest.mark.parametrize(
        "outputs, _transformed_outputs",
        [
            ([], []),
            (["component.property"], Output("component", "property")),
            (
                ["component.property", "component.property"],
                [Output("component", "property"), Output("component", "property")],
            ),
        ],
    )
    def test_outputs_valid(self, identity_action_function, outputs, _transformed_outputs, runtime_inputs):
        action = Action(function=identity_action_function(*runtime_inputs), outputs=outputs)

        assert action.outputs == outputs
        assert action._transformed_outputs == _transformed_outputs

    # The "runtime_inputs" is added here to test outputs for both legacy and non-legacy actions
    @pytest.mark.parametrize("runtime_inputs", [[], ["hardcoded_input"]])
    @pytest.mark.parametrize(
        "outputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_outputs_invalid(self, outputs, identity_action_function, runtime_inputs):
        with pytest.raises(ValidationError, match="String should match pattern"):
            Action(function=identity_action_function(*runtime_inputs), outputs=outputs)


class TestActionBuild:
    def test_custom_action_build(self, identity_action_function):
        action_id = "action_test"
        action = Action(id=action_id, function=identity_action_function())

        assert_component_equal(
            action.build(), html.Div(id=f"{action_id}_action_model_components_div", children=[], hidden=True)
        )


class TestActionCallbackFunction:
    """Test action callback function."""

    @pytest.mark.parametrize(
        "custom_action_mock_return, callback_outputs",
        [
            # no outputs
            (None, []),
            (None, {}),
            (None, None),
            # single output - note this is not [Output(...)] in a list
            (None, Output("component", "property")),
            (["value_1", "value_2"], Output("component", "property")),
            ({"key_1": "value_1"}, Output("component", "property")),
            ("abc", Output("component", "property")),
            # multiple list outputs
            ("ab", [Output("component_1", "property"), Output("component_2", "property")]),
            (["value_1", "value_2"], [Output("component_1", "property"), Output("component_2", "property")]),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                [Output("component", "property"), Output("component_2", "property")],
            ),
            # multiple dict outputs
            ({"component_1": "value_1"}, {"component_1": Output("component", "property")}),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                {"component_1": Output("component_1", "property"), "component_2": Output("component_2", "property")},
            ),
        ],
        indirect=["custom_action_mock_return"],
    )
    def test_action_callback_function_return_value_valid(self, custom_action_mock_return, callback_outputs):
        action = Action(function=custom_action_mock_return())
        # If no error is raised by _action_callback_function then running it should return exactly the same
        # as the output of the custom_action_mock_return.
        assert action._action_callback_function(inputs={}, outputs=callback_outputs) == custom_action_mock_return()()

    @pytest.mark.parametrize("callback_outputs", [[], {}, None])
    @pytest.mark.parametrize("custom_action_mock_return", [False, 0, "", [], (), {}], indirect=True)
    def test_action_callback_function_no_outputs_return_value_not_none(
        self, custom_action_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_mock_return())
        with pytest.raises(
            ValueError, match="Action function has returned a value but the action has no defined outputs."
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize("custom_action_mock_return", [None, False, 0, 123], indirect=True)
    def test_action_callback_function_outputs_list_return_value_not_collection(self, custom_action_mock_return):
        # Note it's not possible for _action_callback_function to be called with a single Output in a list, like
        # [Output(...)]. This would always be done as Output(...) outside a list instead.
        action = Action(function=custom_action_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a list-like object but the action's defined outputs are a list.",
        ):
            action._action_callback_function(
                inputs={}, outputs=[Output("component_1", "property"), Output("component_2", "property")]
            )

    @pytest.mark.parametrize(
        "custom_action_mock_return",
        [None, False, 0, 123, "", [], ()],
        indirect=["custom_action_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_not_mapping(self, custom_action_mock_return):
        action = Action(function=custom_action_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a dictionary-like object "
            "but the action's defined outputs are a dictionary.",
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})

    @pytest.mark.parametrize(
        "custom_action_mock_return",
        ["", [], (), {}, "abc", [1, 2, 3], (1, 2, 3), {"a": 1, "b": 2, "c": 3}],
        indirect=["custom_action_mock_return"],
    )
    def test_action_callback_function_outputs_list_return_value_length_not_match(self, custom_action_mock_return):
        action = Action(function=custom_action_mock_return())
        with pytest.raises(
            ValueError,
            match="Number of action's returned elements .+ does not match the number of action's defined outputs 2.",
        ):
            action._action_callback_function(
                inputs={}, outputs=[Output("component_1", "property"), Output("component_2", "property")]
            )

    @pytest.mark.parametrize(
        "custom_action_mock_return",
        [{}, {"another_output": 1}, {"output": 1, "another_output": 2}],
        indirect=["custom_action_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_keys_not_match(self, custom_action_mock_return):
        action = Action(function=custom_action_mock_return())
        with pytest.raises(
            ValueError, match="Keys of action's returned value .+ do not match the action's defined outputs {'output'}."
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})
