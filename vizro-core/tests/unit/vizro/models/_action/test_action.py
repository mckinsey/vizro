"""Unit tests for vizro.models.Action."""

import sys

import pandas as pd
import pytest
from dash import Output, State, html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
import vizro.plotly.express as px
from asserts import assert_component_equal
from vizro import Vizro
from vizro.actions import export_data
from vizro.managers import model_manager
from vizro.models._action._action import Action
from vizro.models.types import capture


@pytest.fixture
def custom_action_function_mock_return(request):
    @capture("action")
    def _custom_action_function_mock_return():
        return request.param

    return _custom_action_function_mock_return


@pytest.fixture
def custom_action_build_expected():
    return html.Div(id="action_test_action_model_components_div", children=[], hidden=True)


@pytest.fixture
def predefined_action_build_expected():
    return html.Div(id="filter_action_test_filter_action_model_components_div", children=[], hidden=True)


class TestActionInstantiation:
    """Tests model instantiation."""

    def test_create_action_mandatory_only(self, identity_action_function):
        function = identity_action_function()
        action = Action(function=function)

        assert hasattr(action, "id")
        assert action.function is function
        assert action.inputs == []
        assert action.outputs == []

    def test_create_action_mandatory_and_optional(self, identity_action_function):
        function = identity_action_function()
        inputs = ["component_1.property_A", "component_1.property_B"]
        outputs = ["component_2.property_A", "component_2.property_B"]

        action = Action(function=function, inputs=inputs, outputs=outputs)

        assert hasattr(action, "id")
        assert action.function is function
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
    def test_inputs_outputs_valid(self, inputs, outputs, identity_action_function):
        action = Action(function=identity_action_function(), inputs=inputs, outputs=outputs)

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
    def test_inputs_invalid(self, inputs, identity_action_function):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Action(function=identity_action_function(), inputs=inputs, outputs=[])

    @pytest.mark.parametrize(
        "outputs",
        [
            [""],
            ["component"],
            ["component_property"],
            ["component.property.property"],
        ],
    )
    def test_outputs_invalid(self, outputs, identity_action_function):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Action(function=identity_action_function(), inputs=[], outputs=outputs)

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


@pytest.fixture
def managers_one_page_without_graphs_one_button():
    """Instantiates a simple model_manager and data_manager with a page, and no graphs."""
    vm.Page(
        id="test_page",
        title="Test page",
        components=[vm.Graph(figure=px.scatter(data_frame=pd.DataFrame(columns=["A"]), x="A", y="A"))],
        controls=[vm.Filter(id="test_filter", column="A")],
    )
    Vizro._pre_build()


# TODO: improve these tests to check that actual callback is registered.
# In general, we should aim to make all the tests in TestActionBuild and TestActionPrivateMethods
# higher level and more "real" so that we're testing actual callback execution and not just private
# helper methods.
class TestActionBuild:
    """Tests action build method."""

    def test_custom_action_build(self, identity_action_function, custom_action_build_expected):
        action = Action(id="action_test", function=identity_action_function()).build()
        assert_component_equal(action, custom_action_build_expected)

    @pytest.mark.usefixtures("managers_one_page_without_graphs_one_button")
    def test_predefined_export_data_action_build(self, predefined_action_build_expected):
        predefined_filter_action = model_manager["test_page"].controls[0].selector.actions[0].actions[0].build()
        assert_component_equal(predefined_filter_action, predefined_action_build_expected)


class TestActionPrivateMethods:
    """Test action private methods."""

    def test_get_callback_mapping_no_inputs_no_outputs(self, identity_action_function):
        action = Action(function=identity_action_function())
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == {}
        assert callback_outputs == {}
        assert action_components == []

    @pytest.mark.parametrize(
        "inputs_and_outputs, expected_get_callback_mapping_inputs, expected_get_callback_mapping_outputs",
        [
            (["component.property"], [State("component", "property")], Output("component", "property")),
            (
                ["component_1.property", "component_2.property"],
                [State("component_1", "property"), State("component_2", "property")],
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
        ],
    )
    def test_get_callback_mapping_with_inputs_and_outputs(  # pylint: disable=too-many-arguments
        self,
        inputs_and_outputs,
        identity_action_function,
        expected_get_callback_mapping_inputs,
        expected_get_callback_mapping_outputs,
    ):
        action = Action(function=identity_action_function(), inputs=inputs_and_outputs, outputs=inputs_and_outputs)
        callback_inputs, callback_outputs, action_components = action._get_callback_mapping()
        assert callback_inputs == expected_get_callback_mapping_inputs
        assert callback_outputs == expected_get_callback_mapping_outputs
        assert action_components == []

    @pytest.mark.parametrize("inputs", [["value"], {"arg": "value"}])
    def test_action_callback_function_inputs_args_or_kwargs(self, identity_action_function, inputs):
        action = Action(function=identity_action_function())
        assert action._action_callback_function(inputs=inputs, outputs=Output("component", "property")) == "value"

    @pytest.mark.parametrize(
        "custom_action_function_mock_return, callback_outputs",
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
                {"component_1": "value_1", "component_2_property": "value_2"},
                [Output("component", "property"), Output("component_2", "property")],
            ),
            # multiple dict outputs
            ({"component_1": "value_1"}, {"component_1": Output("component", "property")}),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                {"component_1": Output("component_1", "property"), "component_2": Output("component_2", "property")},
            ),
        ],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_return_value_valid(self, custom_action_function_mock_return, callback_outputs):
        action = Action(function=custom_action_function_mock_return())
        # If no error is raised by _action_callback_function then running it should return exactly the same
        # as the output of the custom_action_function_mock_return.
        assert (
            action._action_callback_function(inputs={}, outputs=callback_outputs)
            == custom_action_function_mock_return()()
        )

    @pytest.mark.parametrize("callback_outputs", [[], {}, None])
    @pytest.mark.parametrize("custom_action_function_mock_return", [False, 0, "", [], (), {}], indirect=True)
    def test_action_callback_function_no_outputs_return_value_not_None(
        self, custom_action_function_mock_return, callback_outputs
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError, match="Action function has returned a value but the action has no defined outputs."
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize(
        "custom_action_function_mock_return", [None, False, 0, 123], indirect=["custom_action_function_mock_return"]
    )
    def test_action_callback_function_outputs_list_return_value_not_collection(
        self, custom_action_function_mock_return
    ):
        # Note it's not possible for _action_callback_function to be called with a single Output in a list, like
        # [Output(...)]. This would always be done as Output(...) outside a list instead.
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a list-like object but the action's defined outputs are a list.",
        ):
            action._action_callback_function(
                inputs={}, outputs=[Output("component_1", "property"), Output("component_2", "property")]
            )

    @pytest.mark.parametrize(
        "custom_action_function_mock_return",
        [None, False, 0, 123, "", [], ()],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_not_mapping(
        self, custom_action_function_mock_return
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Action function has not returned a dictionary-like object "
            "but the action's defined outputs are a dictionary.",
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})

    @pytest.mark.parametrize(
        "custom_action_function_mock_return",
        ["", [], (), {}, "abc", [1, 2, 3], (1, 2, 3), {"a": 1, "b": 2, "c": 3}],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_list_return_value_length_not_match(
        self, custom_action_function_mock_return
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError,
            match="Number of action's returned elements .+ does not match the number of action's defined outputs 2.",
        ):
            action._action_callback_function(
                inputs={}, outputs=[Output("component_1", "property"), Output("component_2", "property")]
            )

    @pytest.mark.parametrize(
        "custom_action_function_mock_return",
        [{}, {"another_output": 1}, {"output": 1, "another_output": 2}],
        indirect=["custom_action_function_mock_return"],
    )
    def test_action_callback_function_outputs_mapping_return_value_keys_not_match(
        self, custom_action_function_mock_return
    ):
        action = Action(function=custom_action_function_mock_return())
        with pytest.raises(
            ValueError, match="Keys of action's returned value .+ do not match the action's defined outputs {'output'}."
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})
