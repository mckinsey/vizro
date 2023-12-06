"""Unit tests for vizro.models.Action."""

import json
import sys

import dash
import plotly
import pytest
from dash import html
from dash._callback_context import context_value
from dash._utils import AttributeDict
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
    return {
        f'{input["component_id"]}_{input["component_property"]}': dash.State(
            input["component_id"], input["component_property"]
        )
        for input in request.param
    }


@pytest.fixture
def expected_get_callback_mapping_outputs(request):
    return {
        f'{output["component_id"]}_{output["component_property"]}': dash.Output(
            output["component_id"], output["component_property"], allow_duplicate=True
        )
        for output in request.param
    }


@pytest.fixture
def callback_context_set_outputs_grouping(request):
    """Mock dash.callback_context that represents outputs grouping for custom action."""
    outputs = request.param

    outputs_grouping = dict.fromkeys(outputs)
    mock_callback_context = {"outputs_grouping": {"action_finished": None, **outputs_grouping}}
    context_value.set(AttributeDict(**mock_callback_context))
    return context_value


@pytest.fixture
def custom_action_build_expected():
    return html.Div(
        children=[],
        id="action_test_action_model_components_div",
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
            "string",
            "component_property",
            "compo-nent.property",
            "component.property_1",
        ],
    )
    def test_inputs_invalid(self, inputs, test_action_function):
        with pytest.raises(ValidationError, match="value is not a valid list"):
            Action(function=test_action_function, inputs=inputs, outputs=[])

    @pytest.mark.parametrize(
        "outputs",
        [
            "string",
            "component_property",
            "compo-nent.property",
            "component.property_1",
        ],
    )
    def test_outputs_invalid(self, outputs, test_action_function):
        with pytest.raises(ValidationError, match="value is not a valid list"):
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
        assert callback_inputs == {
            "trigger": dash.Input({"action_name": "action_test", "type": "action_trigger"}, "data")
        }
        assert callback_outputs == {"action_finished": dash.Output("action_finished", "data")}
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
        assert callback_inputs == {
            **expected_get_callback_mapping_inputs,
            "trigger": dash.Input({"action_name": "action_test", "type": "action_trigger"}, "data"),
        }
        assert callback_outputs == {
            **expected_get_callback_mapping_outputs,
            "action_finished": dash.Output("action_finished", "data"),
        }
        assert action_components == []

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_context_set_outputs_grouping, expected_function_return_value",
        [
            # custom action function return value - None
            (None, [], {"action_finished": None}),
            # custom action function return value - single value
            ("new_value", ["component_1_property"], {"action_finished": None, "component_1_property": "new_value"}),
            # custom action function return value - list of values
            (
                ["new_value", "new_value_2"],
                ["component_1_property", "component_2_property"],
                {"action_finished": None, "component_1_property": "new_value", "component_2_property": "new_value_2"},
            ),
            # custom action function return value - tuple
            (
                ("new_value", "new_value_2"),
                ["component_1_property", "component_2_property"],
                {"action_finished": None, "component_1_property": "new_value", "component_2_property": "new_value_2"},
            ),
            # custom action function return value - dictionary
            (
                {"component_1_property": "new_value"},
                ["component_1_property"],
                {"action_finished": None, "component_1_property": "new_value"},
            ),
        ],
        indirect=["custom_action_function_mock_return", "callback_context_set_outputs_grouping"],
    )
    def test_action_callback_function_return_value_valid(
        self, custom_action_function_mock_return, callback_context_set_outputs_grouping, expected_function_return_value
    ):
        action = Action(function=custom_action_function_mock_return())
        result = action._action_callback_function()
        assert result == expected_function_return_value

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_context_set_outputs_grouping",
        [
            (None, ["component_1_property"]),
            ("new_value", []),
            ("new_value", ["component_1_property", "component_2_property"]),
            (["new_value"], []),
            (["new_value"], ["component_1_property", "component_2_property"]),
            (["new_value", "new_value_2"], ["component_1_property"]),
            ({"component_1_property": "new_value"}, []),
            ({"component_1_property": "new_value"}, ["component_1_property", "component_2_property"]),
            ({"component_1_property": "new_value", "component_2_property": "new_value_2"}, ["component_1_property"]),
        ],
        indirect=True,
    )
    def test_action_callback_function_return_value_invalid(
        self, custom_action_function_mock_return, callback_context_set_outputs_grouping
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Number of action's returned elements .(.?.)"
            " does not match the number of action's defined outputs .(.?.).",
        ):
            action._action_callback_function()
