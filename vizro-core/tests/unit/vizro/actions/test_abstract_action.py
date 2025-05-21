import pytest
from asserts import assert_component_equal
from dash import Output, State, html
from pydantic import ValidationError

from vizro.actions._abstract_action import _AbstractAction


class action_with_no_args(_AbstractAction):
    def function(self):
        pass

    @property
    def outputs(self):
        return []


class action_with_one_static_arg(_AbstractAction):
    arg_1: str

    def function(self):
        pass

    @property
    def outputs(self):
        return []


class action_with_two_static_args(_AbstractAction):
    arg_1: str
    arg_2: str

    def function(self):
        pass

    @property
    def outputs(self):
        return []


class action_with_one_runtime_arg(_AbstractAction):
    arg_1: str

    def function(self, arg_1):
        pass

    @property
    def outputs(self):
        return []


class action_with_two_runtime_args(_AbstractAction):
    arg_1: str
    arg_2: str

    def function(self, arg_1: str, arg_2: str):
        pass

    @property
    def outputs(self):
        return []


class action_with_one_runtime_and_one_static(_AbstractAction):
    runtime_arg: str
    static_arg: str

    def function(self, runtime_arg: str):
        pass

    @property
    def outputs(self):
        return []


class action_with_builtin_runtime_arg(_AbstractAction):
    def function(self, _controls: dict):
        pass

    @property
    def outputs(self):
        return []


@pytest.fixture
def action_with_mock_outputs(request):
    class _action_with_mock_outputs(_AbstractAction):
        def function(self):
            pass

        @property
        def outputs(self):
            return request.param

    return _action_with_mock_outputs


class TestAbstractActionInstantiation:
    """Tests _AbstractAction instantiation."""

    def test_action_mandatory_only(self):
        action = action_with_no_args()

        assert hasattr(action, "id")
        assert hasattr(action, "function")
        assert action.outputs == []

        assert not action._legacy
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._dash_components == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"


class TestAbstractActionInputs:
    @pytest.mark.parametrize(
        "action_class, inputs, expected_transformed_inputs",
        [
            (action_with_no_args, {}, {}),
            (
                action_with_one_static_arg,
                {"arg_1": "anything"},
                {},
            ),
            (
                action_with_two_static_args,
                {"arg_1": "anything", "arg_2": "anything"},
                {},
            ),
            (
                action_with_one_runtime_arg,
                {"arg_1": "component.property"},
                {"arg_1": State("component", "property")},
            ),
            (
                action_with_one_runtime_arg,
                {"arg_1": "known_dropdown_filter_id"},
                {"arg_1": State("known_dropdown_filter_id", "value")},
            ),
            (
                action_with_one_runtime_arg,
                {"arg_1": "known_ag_grid_id.cellClicked"},
                {"arg_1": State("underlying_ag_grid_id", "cellClicked")},
            ),
            (
                action_with_two_runtime_args,
                {"arg_1": "component_1.property_1", "arg_2": "component_2.property_2"},
                {"arg_1": State("component_1", "property_1"), "arg_2": State("component_2", "property_2")},
            ),
            (
                action_with_one_runtime_and_one_static,
                {"runtime_arg": "component_1.property_1", "static_arg": "anything"},
                {"runtime_arg": State("component_1", "property_1")},
            ),
            (
                action_with_builtin_runtime_arg,
                {},
                {
                    "_controls": {
                        "filters": [State("known_dropdown_filter_id", "value")],
                        "parameters": [],
                        "filter_interaction": [],
                    }
                },
            ),
        ],
    )
    def test_inputs_valid(
        self, action_class, inputs, expected_transformed_inputs, manager_for_testing_actions_output_input_prop
    ):
        action = action_class(**inputs)
        assert action._transformed_inputs == expected_transformed_inputs

    @pytest.mark.parametrize(
        "input",
        [
            # These raise validation error on instantiation of action_with_one_runtime_arg due to annotation arg_1: str
            ["component.property"],
            1,
            None,
        ],
    )
    def test_inputs_invalid_type(self, input):
        with pytest.raises(ValidationError):
            action_with_one_runtime_arg(arg_1=input)._transformed_inputs

    @pytest.mark.parametrize(
        "input",
        [
            "unknown_model_id",
        ],
    )
    def test_inputs_invalid_model_id(self, input):
        with pytest.raises(
            KeyError,
            match="Model with ID .* not found. Please provide a valid component ID.",
        ):
            action_with_one_runtime_arg(arg_1=input)._transformed_inputs

    @pytest.mark.parametrize(
        "input",
        [
            "",
            "component.",
            ".property",
            "component..property",
            "component.property.property",
        ],
    )
    def test_inputs_invalid_dot_syntax(self, input):
        with pytest.raises(
            ValueError,
            match="Invalid input format .*. Expected format is '<model_id>' or '<model_id>.<argument_name>'.",
        ):
            action_with_one_runtime_arg(arg_1=input)._transformed_inputs

    def test_inputs_invalid_missing_action_attribute(self, manager_for_testing_actions_output_input_prop):
        with pytest.raises(
            AttributeError,
            match="Model with ID 'known_model_with_no_default_props' does not have implicit input properties defined. "
            "Please specify the input explicitly as 'known_model_with_no_default_props.<property>'.",
        ):
            action = action_with_one_runtime_arg(arg_1="known_model_with_no_default_props")._transformed_inputs
            action._transformed_inputs

    # TODO: Adjust this test when _controls becomes a public field. Should demonstrate that a runtime arg called
    # controls overrides the inbuilt behavior. This could be done as a new test case in TestAbstractActionInputs
    # like in test_action.TestActionInputs works.
    @pytest.mark.xfail(reason="Private fields can't be overwritten")
    def test_builtin_runtime_arg_with_overwritten_controls(self):
        action = action_with_builtin_runtime_arg()
        assert action._transformed_inputs == {"_controls": State("component", "property")}


class TestBuiltinRuntimeArgs:
    """Test the actual values of the runtime args are correct in a real scenario."""

    def test_builtin_runtime_arg_controls(self, page_actions_builtin_controls):
        action = action_with_builtin_runtime_arg()
        assert action._transformed_inputs == page_actions_builtin_controls


class TestAbstractActionOutputs:
    @pytest.mark.parametrize(
        "action_with_mock_outputs, expected_transformed_outputs",
        [
            ([], []),
            (["component.property"], Output("component", "property")),
            (
                ["component_1.property_1", "component_2.property_2"],
                [Output("component_1", "property_1"), Output("component_2", "property_2")],
            ),
            (["known_ag_grid_id"], Output("known_ag_grid_id", "children")),
            (["known_ag_grid_id.cellClicked"], Output("underlying_ag_grid_id", "cellClicked")),
            ({}, {}),
            (
                {"output_1": "component.property"},
                {"output_1": Output("component", "property")},
            ),
            (
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": Output("component_1", "property_1"), "output_2": Output("component_2", "property_2")},
            ),
            (
                {"output_1": "known_ag_grid_id"},
                {"output_1": Output("known_ag_grid_id", "children")},
            ),
            (
                {"output_1": "known_ag_grid_id.cellClicked"},
                {"output_1": Output("underlying_ag_grid_id", "cellClicked")},
            ),
        ],
        indirect=["action_with_mock_outputs"],
    )
    def test_outputs_valid(
        self, action_with_mock_outputs, expected_transformed_outputs, manager_for_testing_actions_output_input_prop
    ):
        action = action_with_mock_outputs()
        assert action._transformed_outputs == expected_transformed_outputs

    @pytest.mark.parametrize(
        "action_with_mock_outputs",
        [
            "component.property",
            1,
            None,
            {1: "component.property"},
        ],
        indirect=["action_with_mock_outputs"],
    )
    def test_outputs_invalid_type(self, action_with_mock_outputs):
        with pytest.raises(ValidationError):
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action_with_mock_outputs()._transformed_outputs

    @pytest.mark.parametrize(
        "action_with_mock_outputs",
        [
            ["unknown_model_id"],
            {"output_1": "unknown_model_id"},
        ],
        indirect=["action_with_mock_outputs"],
    )
    def test_outputs_invalid_model_id(self, action_with_mock_outputs):
        with pytest.raises(
            KeyError,
            match="Model with ID .* not found. Please provide a valid component ID.",
        ):
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action_with_mock_outputs()._transformed_outputs

    @pytest.mark.parametrize(
        "action_with_mock_outputs",
        [
            [""],
            ["component."],
            [".property"],
            ["component..property"],
            ["component.property.property"],
            {"output_1": ""},
            {"output_1": "component."},
            {"output_1": ".property"},
            {"output_1": "component..property"},
            {"output_1": "component.property.property"},
            {"output_1": "component.property", "output_2": ""},
        ],
        indirect=["action_with_mock_outputs"],
    )
    def test_outputs_invalid_dot_syntax(self, action_with_mock_outputs):
        with pytest.raises(
            ValueError,
            match="Invalid output format .*. Expected format is '<model_id>' or '<model_id>.<argument_name>'.",
        ):
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action_with_mock_outputs()._transformed_outputs

    def test_outputs_invalid_missing_action_attribute(
        self, manager_for_testing_actions_output_input_prop, action_with_mock_outputs
    ):
        with pytest.raises(
            KeyError,
            match="Model with ID `known_model_with_no_default_props` has no `__default__` key inside its"
            " `_action_outputs` property. Please specify the output explicitly as"
            " `known_model_with_no_default_props.<property>`.",
        ):
            action_with_mock_outputs.outputs = ["known_model_with_no_default_props"]
            action_with_mock_outputs()._transformed_outputs


class TestAbstractActionBuild:
    def test_abstract_action_build(self):
        action = action_with_no_args(id="action_test")
        assert_component_equal(
            action.build(), html.Div(id="action_test_action_model_components_div", children=[], hidden=True)
        )
