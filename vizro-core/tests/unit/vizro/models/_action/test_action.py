"""Unit tests for vizro.models.Action."""

import json
import sys

import dash
import plotly
import pytest
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


from vizro.actions import export_data
from vizro.models._action._action import Action
from vizro.models.types import capture


@pytest.fixture
def custom_action_function_mock_return(request):
    @capture("action")
    def action_function():
        return request.param

    return action_function


@pytest.fixture
def expected_get_callback_mapping_inputs(request):
    return [dash.State(input["component_id"], input["component_property"]) for input in request.param]


@pytest.fixture
def expected_get_callback_mapping_outputs(request):
    outputs = [
        dash.Output(output["component_id"], output["component_property"], allow_duplicate=True)
        for output in request.param
    ]
    if len(outputs) == 1:
        outputs = outputs[0]
    return outputs


@pytest.fixture
def custom_action_build_expected():
    return html.Div(
        children=[],
        id="action_test_action_model_components_div",
        hidden=True,
    )


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

        action = Action(function=test_action_function, inputs=inputs, outputs=outputs)

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
            (
                ["Component_1.Property_A", "Component_2.Property_B"],
                ["Component_1.Property_A", "Component_2.Property_B"],
            ),
        ],
    )
    def test_inputs_outputs_valid(self, inputs, outputs, test_action_function):
        action = Action(function=test_action_function, inputs=inputs, outputs=outputs)

        assert action.inputs == inputs
        assert action.outputs == outputs

    @pytest.mark.parametrize(
        "inputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_inputs_invalid(self, inputs, test_action_function):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Action(function=test_action_function, inputs=inputs, outputs=[])

    @pytest.mark.parametrize(
        "outputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_outputs_invalid(self, outputs, test_action_function):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Action(function=test_action_function, inputs=[], outputs=outputs)

    @pytest.mark.parametrize("file_format", [None, "csv", "xlsx"])
    def test_export_data_file_format_valid(self, file_format):
        action = Action(id="action_test", function=export_data(file_format=file_format))
        assert action.id == "action_test"
        assert action.inputs == []
        assert action.outputs == []

    def test_export_data_file_format_invalid(self):
        with pytest.raises(
            ValueError, match='Unknown "file_format": invalid_file_format.' ' Known file formats: "csv", "xlsx".'
        ):
            Action(function=export_data(file_format="invalid_file_format"))

    def test_export_data_xlsx_without_required_libs_installed(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "openpyxl", None)
        monkeypatch.setitem(sys.modules, "xlswriter", None)

        with pytest.raises(
            ModuleNotFoundError, match="You must install either openpyxl or xlsxwriter to export to xlsx format."
        ):
            Action(function=export_data(file_format="xlsx"))


class TestActionBuild:
    """Tests action build method."""

    def test_custom_action_build(self, test_action_function, custom_action_build_expected):
        action = Action(id="action_test", function=test_action_function)
        result = json.loads(json.dumps(action.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(custom_action_build_expected, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected


class TestActionPrivateMethods:
    """Test action private methods."""

    def test_get_callback_mapping_no_inputs_no_outputs(self, test_action_function):
        action = Action(id="action_test", function=test_action_function)
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == {}
        assert callback_outputs == {}
        assert action_components == []

    @pytest.mark.parametrize(
        "inputs_and_outputs, expected_get_callback_mapping_inputs, expected_get_callback_mapping_outputs",
        [
            (
                ["component_1.property"],
                [{"component_id": "component_1", "component_property": "property"}],
                [{"component_id": "component_1", "component_property": "property"}],
            ),
            (
                ["component_1.property", "component_2.property"],
                [
                    {"component_id": "component_1", "component_property": "property"},
                    {"component_id": "component_2", "component_property": "property"},
                ],
                [
                    {"component_id": "component_1", "component_property": "property"},
                    {"component_id": "component_2", "component_property": "property"},
                ],
            ),
        ],
        indirect=["expected_get_callback_mapping_inputs", "expected_get_callback_mapping_outputs"],
    )
    def test_get_callback_mapping_with_inputs_and_outputs(  # pylint: disable=too-many-arguments
        self,
        inputs_and_outputs,
        test_action_function,
        expected_get_callback_mapping_inputs,
        expected_get_callback_mapping_outputs,
    ):
        action = Action(
            id="action_test",
            function=test_action_function,
            inputs=inputs_and_outputs,
            outputs=inputs_and_outputs,
        )
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == expected_get_callback_mapping_inputs
        assert callback_outputs == expected_get_callback_mapping_outputs
        assert action_components == []

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs, expected_function_return_value",
        [
            # no outputs
            (None, [], None),
            (None, {}, None),
            (None, None, None),
            # single output
            (None, "component_1_property", None),
            (False, "component_1_property", False),
            (0, "component_1_property", 0),
            (123, "component_1_property", 123),
            ("value", "component_1_property", "value"),
            ((), "component_1_property", ()),
            (("value"), "component_1_property", ("value")),
            (("value_1", "value_2"), "component_1_property", ("value_1", "value_2")),
            ([], "component_1_property", []),
            (["value"], "component_1_property", ["value"]),
            (["value_1", "value_2"], "component_1_property", ["value_1", "value_2"]),
            ({}, "component_1_property", {}),
            ({"key_1": "value_1"}, "component_1_property", {"key_1": "value_1"}),
            (
                {"key_1": "value_1", "key_2": "value_2"},
                "component_1_property",
                {"key_1": "value_1", "key_2": "value_2"},
            ),
            # multiple list outputs
            ("ab", ["component_1_property", "component_2_property"], "ab"),
            (
                ("value_1", "value_2"),
                ["component_1_property", "component_2_property"],
                ("value_1", "value_2"),
            ),
            (
                ["value_1", "value_2"],
                ["component_1_property", "component_2_property"],
                ["value_1", "value_2"],
            ),
            (
                {"component_1_property": "value_1", "component_2_property": "value_2"},
                ["component_1_property", "component_2_property"],
                {"component_1_property": "value_1", "component_2_property": "value_2"},
            ),
            # multiple mapping outputs
            (
                {"component_1": "value_1"},
                {"component_1": "value"},
                {"component_1": "value_1"},
            ),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                {"component_1": "value", "component_2": "value"},
                {"component_1": "value_1", "component_2": "value_2"},
            ),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                {"component_2": "value", "component_1": "value"},
                {"component_1": "value_1", "component_2": "value_2"},
            ),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_return_value_valid(
        self, custom_action_function_mock_return, callback_outputs, expected_function_return_value
    ):
        action = Action(function=custom_action_function_mock_return())
        result = action._action_callback_function(inputs={}, outputs=callback_outputs)
        assert result == expected_function_return_value

    @pytest.mark.parametrize("callback_outputs", [[], {}, None])
    @pytest.mark.parametrize(
        "custom_action_function_mock_return",
        [False, 0, "", [], (), {}],
        indirect=True,
    )
    def test_action_callback_function_no_outputs_return_value_exists(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has returned a value but the action has no defined outputs.",
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs",
        [
            (None, ["component_1_property"]),
            (False, ["component_1_property"]),
            (0, ["component_1_property"]),
            (123, ["component_1_property"]),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_list_return_value_not_collection(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a list or similar but the action's defined outputs are a list.",
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs",
        [
            (None, {"component_1_property": "value"}),
            (False, {"component_1_property": "value"}),
            (0, {"component_1_property": "value"}),
            (123, {"component_1_property": "value"}),
            ("", {"component_1_property": "value"}),
            ([], {"component_1_property": "value"}),
            ((), {"component_1_property": "value"}),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_not_mapping(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a dictionary or similar "
            "but the action's defined outputs are a dictionary.",
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs",
        [
            ("", ["component_1_property"]),
            ([], ["component_1_property"]),
            ((), ["component_1_property"]),
            ({}, ["component_1_property"]),
            ("12", ["component_1_property"]),
            ([1, 2], ["component_1_property"]),
            ((1, 2), ["component_1_property"]),
            ({"a": 1, "b": 2}, ["component_1_property"]),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_list_return_value_length_not_match(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Number of action's returned elements .+ does not match the number of action's defined outputs .+",
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs",
        [
            ({}, {"component_1_property": "value"}),
            ({"a": 1, "b": 2}, {"component_1_property": "value"}),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_keys_not_match(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Keys of action's returned value .+ do not match the action's defined outputs .+",
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)
