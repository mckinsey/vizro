"""Unit tests for vizro.models.Action."""

import pytest
from asserts import assert_component_equal
from dash import Output, State, dcc, no_update
from pydantic import ValidationError

from vizro.actions import show_notification, update_notification
from vizro.models._action._action import Action
from vizro.models.types import _get_action_discriminator, capture


@capture("action")
def action_with_no_args():
    pass


@capture("action")
def action_with_one_arg(arg_1):
    pass


@capture("action")
def action_with_two_args(arg_1, arg_2):
    pass


@capture("action")
def action_with_builtin_runtime_args(arg_1, _trigger, _controls):
    pass


@pytest.fixture
def action_with_mock_return_value(request):
    @capture("action")
    def _action_with_mock_return_value():
        return request.param

    return _action_with_mock_return_value


@pytest.mark.filterwarnings("ignore:The `inputs` argument is deprecated:FutureWarning")
class TestLegacyActionInstantiation:
    def test_action_first_in_chain_mandatory_only(self):
        function = action_with_no_args()

        # inputs=[] added to force action to be legacy
        action = Action(id="action-id", function=function, inputs=[])

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.inputs == []
        assert action.outputs == []

        # default error notification
        assert len(action.notifications) == 1
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == show_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True

        assert action._legacy
        assert_component_equal(
            action._dash_components, [dcc.Store(id="action-id_finished"), dcc.Store(id="action-id_guarded_trigger")]
        )
        assert action._transformed_inputs == []
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"

    def test_action_not_first_in_chain_mandatory_only(self):
        function = action_with_no_args()

        # inputs=[] added to force action to be legacy
        action = Action(id="action-id", function=function, inputs=[])

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = "trigger.property"
        action._trigger = "trigger_2.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.inputs == []
        assert action.outputs == []

        # default error notification
        assert len(action.notifications) == 1
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == show_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True

        assert action._legacy
        assert_component_equal(action._dash_components, [dcc.Store(id="action-id_finished")])
        assert action._transformed_inputs == []
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"

    def test_action_first_in_chain_with_progress_notification(self):
        function = action_with_no_args()

        # inputs=[] added to force action to be legacy
        action = Action(id="action-id", function=function, inputs=[], notifications={"progress": "Progress."})

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.inputs == []
        assert action.outputs == []

        assert len(action.notifications) == 2
        # progress notification
        result_progress_notification = action.notifications["progress"]
        assert type(result_progress_notification) == show_notification
        assert result_progress_notification.variant == "progress"
        assert result_progress_notification.text == "Progress."
        assert result_progress_notification._is_conditional is True
        # default error notification - update_notification
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == update_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True
        assert result_error_notification.notification == result_progress_notification.id

        assert action._legacy
        assert_component_equal(
            action._dash_components,
            [
                dcc.Store(id="action-id_finished"),
                dcc.Store(id="action-id_guarded_trigger"),
                dcc.Store(id="action-id_progress_notification_object", data=result_progress_notification.function()),
                dcc.Store(id="action-id_action_parameters", data=[]),
            ],
        )
        assert action._transformed_inputs == []
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"

    def test_inputs_deprecated(self):
        with pytest.warns(FutureWarning, match="The `inputs` argument is deprecated"):
            Action(function=action_with_no_args(), inputs=[])

    def test_action_deprecated_yaml(self):
        # Test dictionary configuration of an action without discriminator "type" specified. The behavior here should
        # be equivalent to specifying vm.Action but with an extra warning. Ideally we would test this using the higher
        # level ActionsType, analogous to test_layout_deprecated_yaml, but that means resolving lots of ForwardRefs here
        # which is not worth the effort.
        with pytest.warns(FutureWarning, match="Action without an explicit `type` specified"):
            action_tag = _get_action_discriminator({"function": {"_target_": "export_data"}})

        assert action_tag == "action"


@pytest.mark.filterwarnings("ignore:The `inputs` argument is deprecated:FutureWarning")
class TestLegacyActionInputs:
    @pytest.mark.parametrize(
        "action_function, runtime_inputs, expected_transformed_inputs",
        [
            (action_with_no_args, [], []),
            (action_with_one_arg, ["component.property"], [State("component", "property")]),
            (action_with_one_arg, ["known_dropdown_filter_id"], [State("known_dropdown_filter_id", "value")]),
            (action_with_one_arg, ["known_ag_grid_id.cellClicked"], [State("underlying_ag_grid_id", "cellClicked")]),
            (
                action_with_two_args,
                ["component_1.property_1", "component_2.property_2"],
                [State("component_1", "property_1"), State("component_2", "property_2")],
            ),
        ],
    )
    def test_action_inputs_valid(
        self,
        action_function,
        runtime_inputs,
        expected_transformed_inputs,
        manager_for_testing_actions_output_input_prop,
    ):
        action = Action(function=action_function(), inputs=runtime_inputs)

        assert action._legacy
        assert action.inputs == runtime_inputs
        assert action._transformed_inputs == expected_transformed_inputs

    @pytest.mark.parametrize(
        "runtime_inputs",
        [
            ["unknown_model_id"],
        ],
    )
    def test_action_inputs_invalid_model_id(self, runtime_inputs):
        with pytest.raises(KeyError, match=r"Model with ID .* not found. Provide a valid component ID\."):
            action = Action(function=action_with_one_arg(), inputs=runtime_inputs)
            action._transformed_inputs

    @pytest.mark.parametrize(
        "runtime_inputs",
        [
            [""],
            ["component."],
            [".property"],
            ["component..property"],
            ["component.property.property"],
        ],
    )
    def test_action_inputs_invalid_dot_syntax(self, runtime_inputs):
        with pytest.raises(
            ValueError,
            match=r"Invalid input format .*. Expected format is '<model_id>' or '<model_id>.<argument_name>'\.",
        ):
            action = Action(function=action_with_one_arg(), inputs=runtime_inputs)
            action._transformed_inputs

    def test_inputs_invalid_missing_action_attribute(self, manager_for_testing_actions_output_input_prop):
        with pytest.raises(
            AttributeError,
            match=r"Model with ID 'known_model_with_no_default_props' does not have implicit input properties defined. "
            r"Specify the input explicitly as 'known_model_with_no_default_props.<property>'.",
        ):
            action = Action(function=action_with_one_arg(), inputs=["known_model_with_no_default_props"])
            action._transformed_inputs

    @pytest.mark.parametrize(
        "static_inputs",
        [
            "",
            "component",
            "component.",
            ".property",
            "component..property",
            "component.property.property",
        ],
    )
    @pytest.mark.filterwarnings("ignore:Passing a static argument to a custom action is deprecated:FutureWarning")
    def test_static_inputs(self, static_inputs):
        action = Action(function=action_with_one_arg(static_inputs))

        assert action._legacy
        assert action.inputs == []
        assert action._transformed_inputs == []

    def test_static_inputs_deprecated(self):
        action = Action(function=action_with_one_arg(""))
        with pytest.warns(FutureWarning, match="Passing a static argument to a custom action is deprecated"):
            action._transformed_inputs

    @pytest.mark.parametrize(
        "action_function, static_inputs, runtime_inputs, expected_transformed_inputs",
        [
            (action_with_one_arg, {}, ["component.property"], [State("component", "property")]),
            (action_with_one_arg, {"arg_1": "hardcoded"}, [], []),
            (
                action_with_two_args,
                {"arg_1": "hardcoded"},
                ["component.property"],
                [State("component", "property")],
            ),
            (
                action_with_two_args,
                {"arg_1": "component.property"},
                ["component.property"],
                [State("component", "property")],
            ),
        ],
    )
    @pytest.mark.filterwarnings("ignore:Passing a static argument to a custom action is deprecated:FutureWarning")
    def test_mixed_static_and_runtime_inputs(
        self,
        action_function,
        static_inputs,
        runtime_inputs,
        expected_transformed_inputs,
    ):
        action = Action(function=action_function(**static_inputs), inputs=runtime_inputs)

        assert action._legacy
        assert action.inputs == runtime_inputs
        assert action._transformed_inputs == expected_transformed_inputs


@pytest.mark.filterwarnings("ignore:The `inputs` argument is deprecated:FutureWarning")
class TestLegacyActionOutputs:
    @pytest.mark.parametrize(
        "outputs, expected_outputs, expected_transformed_outputs",
        [
            ([], [], []),
            ("component.property", ["component.property"], Output("component", "property")),
            ("known_ag_grid_id", ["known_ag_grid_id"], Output("known_ag_grid_id", "children")),
            (
                "known_ag_grid_id.cellClicked",
                ["known_ag_grid_id.cellClicked"],
                Output("underlying_ag_grid_id", "cellClicked"),
            ),
            (["component.property"], ["component.property"], Output("component", "property")),
            (
                ["component_1.property_1", "component_2.property_2"],
                ["component_1.property_1", "component_2.property_2"],
                [Output("component_1", "property_1"), Output("component_2", "property_2")],
            ),
            (["known_ag_grid_id"], ["known_ag_grid_id"], Output("known_ag_grid_id", "children")),
            (
                ["known_ag_grid_id.cellClicked"],
                ["known_ag_grid_id.cellClicked"],
                Output("underlying_ag_grid_id", "cellClicked"),
            ),
            ({}, {}, {}),
            (
                {"output_1": "component.property"},
                {"output_1": "component.property"},
                {"output_1": Output("component", "property")},
            ),
            (
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": Output("component_1", "property_1"), "output_2": Output("component_2", "property_2")},
            ),
            (
                {"output_1": "known_ag_grid_id"},
                {"output_1": "known_ag_grid_id"},
                {"output_1": Output("known_ag_grid_id", "children")},
            ),
            (
                {"output_1": "known_ag_grid_id.cellClicked"},
                {"output_1": "known_ag_grid_id.cellClicked"},
                {"output_1": Output("underlying_ag_grid_id", "cellClicked")},
            ),
            ("vizro_download", ["vizro_download"], Output("vizro_download", "data")),
            (["vizro_download"], ["vizro_download"], Output("vizro_download", "data")),
            (
                {"output_1": "vizro_download"},
                {"output_1": "vizro_download"},
                {"output_1": Output("vizro_download", "data")},
            ),
        ],
    )
    def test_outputs_valid(
        self, outputs, expected_outputs, expected_transformed_outputs, manager_for_testing_actions_output_input_prop
    ):
        # inputs=[] added to force action to be legacy
        action = Action(function=action_with_no_args(), inputs=[], outputs=outputs)

        assert action._legacy
        assert action.outputs == expected_outputs
        assert action._transformed_outputs == expected_transformed_outputs

    @pytest.mark.parametrize(
        "outputs",
        [
            "unknown_model_id",
            ["unknown_model_id"],
            {"output_1": "unknown_model_id"},
        ],
    )
    def test_outputs_invalid_model_id(self, outputs):
        with pytest.raises(
            KeyError,
            match=r"Model with ID .* not found. Provide a valid component ID\.",
        ):
            # inputs=[] added to force action to be legacy
            action = Action(function=action_with_no_args(), inputs=[], outputs=outputs)
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action._transformed_outputs

    @pytest.mark.parametrize(
        "outputs",
        [
            "",
            "component.",
            ".property",
            "component..property",
            "component.property.property",
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
    )
    def test_outputs_invalid_dot_syntax(self, outputs):
        with pytest.raises(
            ValueError,
            match=r"Invalid output format .*. Expected format is '<model_id>' or '<model_id>.<argument_name>'\.",
        ):
            # inputs=[] added to force action to be legacy
            action = Action(function=action_with_no_args(), inputs=[], outputs=outputs)
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action._transformed_outputs

    def test_outputs_invalid_missing_action_attribute(self, manager_for_testing_actions_output_input_prop):
        with pytest.raises(
            KeyError,
            match=r"Model with ID `known_model_with_no_default_props` has no `__default__` key inside its"
            " `_action_outputs` property. Specify the output explicitly as"
            r" `known_model_with_no_default_props.<property>`\.",
        ):
            # inputs=[] added to force action to be legacy
            action = Action(function=action_with_no_args(), inputs=[], outputs=["known_model_with_no_default_props"])
            action._transformed_outputs


@pytest.mark.filterwarnings("ignore:The `inputs` argument is deprecated:FutureWarning")
class TestIsActionLegacy:
    """Tests action._legacy property."""

    @pytest.mark.parametrize("runtime_as_kwargs", [True, False])
    @pytest.mark.parametrize(
        "action_function, static_inputs, runtime_inputs, expected_legacy",
        [
            # No args
            (action_with_no_args, {}, [], False),
            # One arg
            (action_with_one_arg, {}, ["component.property"], True),
            (action_with_one_arg, {"arg_1": "hardcoded"}, [], True),
            (action_with_one_arg, {"arg_1": "component.property"}, [], False),
            (action_with_one_arg, {}, ["known_ag_grid_id"], True),
            (action_with_one_arg, {"arg_1": "known_ag_grid_id"}, [], False),
            # Two args
            (action_with_two_args, {}, ["component.property", "component.property"], True),
            (action_with_two_args, {"arg_1": "component.property"}, ["component.property"], True),
            (action_with_two_args, {"arg_1": "component.property", "arg_2": "hardcoded"}, [], True),
            (action_with_two_args, {"arg_1": "component.property", "arg_2": "component.property"}, [], False),
        ],
    )
    @pytest.mark.filterwarnings("ignore:Passing a static argument to a custom action is deprecated:FutureWarning")
    def test_mixed_runtime_and_runtime_inputs(
        self,
        runtime_as_kwargs,
        action_function,
        static_inputs,
        runtime_inputs,
        expected_legacy,
        manager_for_testing_actions_output_input_prop,
    ):
        function = action_function(**static_inputs) if runtime_as_kwargs else action_function(*static_inputs.values())

        # Conditionally set model field inputs only if not empty so we don't stick with legacy actions only.
        action = Action(function=function, inputs=runtime_inputs) if runtime_inputs else Action(function=function)

        assert action._legacy == expected_legacy


class TestActionInstantiation:
    """Tests model instantiation."""

    def test_action_first_in_chain_mandatory_only(self):
        function = action_with_no_args()
        action = Action(id="action-id", function=function)

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.outputs == []

        # default error notification
        assert len(action.notifications) == 1
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == show_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True

        assert_component_equal(
            action._dash_components, [dcc.Store(id="action-id_finished"), dcc.Store(id="action-id_guarded_trigger")]
        )
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"

    def test_action_not_first_in_chain_mandatory_only(self):
        function = action_with_no_args()
        action = Action(id="action-id", function=function)

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = "trigger.property"
        action._trigger = "trigger_2.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.outputs == []

        # default error notification
        assert len(action.notifications) == 1
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == show_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True

        assert_component_equal(action._dash_components, [dcc.Store(id="action-id_finished")])
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"

    def test_action_first_in_chain_with_progress_notification(self):
        function = action_with_no_args()
        action = Action(id="action-id", function=function, notifications={"progress": "Progress."})

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        assert hasattr(action, "id")
        assert action.function is function
        assert action.outputs == []

        assert len(action.notifications) == 2
        # progress notification
        result_progress_notification = action.notifications["progress"]
        assert type(result_progress_notification) == show_notification
        assert result_progress_notification.variant == "progress"
        assert result_progress_notification.text == "Progress."
        assert result_progress_notification._is_conditional is True
        # default error notification - update_notification
        result_error_notification = action.notifications["error"]
        assert type(result_error_notification) == update_notification
        assert result_error_notification.variant == "error"
        assert result_error_notification.text == "Action failed."
        assert result_error_notification._is_conditional is True
        assert result_error_notification.notification == result_progress_notification.id

        assert_component_equal(
            action._dash_components,
            [
                dcc.Store(id="action-id_finished"),
                dcc.Store(id="action-id_guarded_trigger"),
                dcc.Store(id="action-id_progress_notification_object", data=result_progress_notification.function()),
                dcc.Store(id="action-id_action_parameters", data=[]),
            ],
        )
        assert action._transformed_inputs == {}
        assert action._transformed_outputs == []
        assert action._parameters == set()
        assert action._runtime_args == {}
        assert action._action_name == "action_with_no_args"


class TestActionInputs:
    @pytest.mark.parametrize(
        "action_function, inputs, expected_transformed_inputs",
        [
            (action_with_no_args, {}, {}),
            (action_with_one_arg, {"arg_1": "component.property"}, {"arg_1": State("component", "property")}),
            (
                action_with_one_arg,
                {"arg_1": "known_dropdown_filter_id"},
                {"arg_1": State("known_dropdown_filter_id", "value")},
            ),
            (
                action_with_one_arg,
                {"arg_1": "known_ag_grid_id.cellClicked"},
                {"arg_1": State("underlying_ag_grid_id", "cellClicked")},
            ),
            (
                action_with_two_args,
                {"arg_1": "component.property", "arg_2": "component.property"},
                {"arg_1": State("component", "property"), "arg_2": State("component", "property")},
            ),
            (
                action_with_builtin_runtime_args,
                {},
                {
                    "_controls": {
                        "filters": [State("known_dropdown_filter_id", "value")],
                        "parameters": [],
                        "filter_interaction": [],
                    },
                    "_trigger": State("trigger", "property"),
                },
            ),
            (
                # Case that a builtin runtime argument is overridden by a user supplied one.
                action_with_builtin_runtime_args,
                {"_controls": "component.property"},
                {"_controls": State("component", "property"), "_trigger": State("trigger", "property")},
            ),
        ],
    )
    def test_inputs_valid(
        self, action_function, inputs, expected_transformed_inputs, manager_for_testing_actions_output_input_prop
    ):
        action = Action(function=action_function(**inputs))

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        assert action._transformed_inputs == expected_transformed_inputs

    @pytest.mark.parametrize(
        "input",
        [
            ["component.property"],
            1,
            None,
            "",
            "component",
            "component.",
            ".property",
            "component..property",
            "component.property.property",
        ],
    )
    @pytest.mark.xfail(reason="Validation will only be performed once legacy actions are removed")
    def test_runtime_inputs_invalid(self, input):
        action = Action(function=action_with_one_arg(input))

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        with pytest.raises(ValidationError):
            action._transformed_inputs

    def test_inputs_invalid_missing_action_attribute(self, manager_for_testing_actions_output_input_prop):
        with pytest.raises(
            AttributeError,
            match=r"Model with ID 'known_model_with_no_default_props' does not have implicit input properties defined. "
            r"Specify the input explicitly as 'known_model_with_no_default_props.<property>'.",
        ):
            action = Action(function=action_with_one_arg("known_model_with_no_default_props"))

            # Mock private attribute set by parent component's validation, not Action's.
            action._first_in_chain_trigger = action._trigger = "trigger.property"

            action._transformed_inputs


class TestBuiltinRuntimeArgs:
    """Test the actual values of the runtime args are correct in a real scenario."""

    @pytest.mark.filterwarnings("ignore:`filter_interaction` is deprecated:FutureWarning")
    def test_builtin_runtime_arg_controls_legacy(self, page_actions_builtin_controls_legacy):
        action = Action(function=action_with_builtin_runtime_args())

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        expected_transformed_input = {
            **page_actions_builtin_controls_legacy,
            "_trigger": State("trigger", "property"),
        }

        assert action._transformed_inputs == expected_transformed_input

    def test_builtin_runtime_arg_controls(self, page_actions_builtin_controls):
        action = Action(function=action_with_builtin_runtime_args())

        # Mock private attribute set by parent component's validation, not Action's.
        action._first_in_chain_trigger = action._trigger = "trigger.property"

        expected_transformed_input = {
            **page_actions_builtin_controls,
            "_trigger": State("trigger", "property"),
        }

        assert action._transformed_inputs == expected_transformed_input


class TestActionOutputs:
    @pytest.mark.parametrize(
        "outputs, expected_outputs, expected_transformed_outputs",
        [
            ([], [], []),
            ("component.property", ["component.property"], Output("component", "property")),
            ("known_ag_grid_id", ["known_ag_grid_id"], Output("known_ag_grid_id", "children")),
            (
                "known_ag_grid_id.cellClicked",
                ["known_ag_grid_id.cellClicked"],
                Output("underlying_ag_grid_id", "cellClicked"),
            ),
            (["component.property"], ["component.property"], Output("component", "property")),
            (
                ["component_1.property_1", "component_2.property_2"],
                ["component_1.property_1", "component_2.property_2"],
                [Output("component_1", "property_1"), Output("component_2", "property_2")],
            ),
            (["known_ag_grid_id"], ["known_ag_grid_id"], Output("known_ag_grid_id", "children")),
            (
                ["known_ag_grid_id.cellClicked"],
                ["known_ag_grid_id.cellClicked"],
                Output("underlying_ag_grid_id", "cellClicked"),
            ),
            ({}, {}, {}),
            (
                {"output_1": "component.property"},
                {"output_1": "component.property"},
                {"output_1": Output("component", "property")},
            ),
            (
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": "component_1.property_1", "output_2": "component_2.property_2"},
                {"output_1": Output("component_1", "property_1"), "output_2": Output("component_2", "property_2")},
            ),
            (
                {"output_1": "known_ag_grid_id"},
                {"output_1": "known_ag_grid_id"},
                {"output_1": Output("known_ag_grid_id", "children")},
            ),
            (
                {"output_1": "known_ag_grid_id.cellClicked"},
                {"output_1": "known_ag_grid_id.cellClicked"},
                {"output_1": Output("underlying_ag_grid_id", "cellClicked")},
            ),
            ("vizro_download", ["vizro_download"], Output("vizro_download", "data")),
            (["vizro_download"], ["vizro_download"], Output("vizro_download", "data")),
            (
                {"output_1": "vizro_download"},
                {"output_1": "vizro_download"},
                {"output_1": Output("vizro_download", "data")},
            ),
        ],
    )
    def test_outputs_valid(
        self, outputs, expected_outputs, expected_transformed_outputs, manager_for_testing_actions_output_input_prop
    ):
        action = Action(function=action_with_no_args(), outputs=outputs)

        assert action.outputs == expected_outputs
        assert action._transformed_outputs == expected_transformed_outputs

    @pytest.mark.parametrize(
        "outputs",
        [
            "unknown_model_id",
            ["unknown_model_id"],
            {"output_1": "unknown_model_id"},
        ],
    )
    def test_outputs_invalid_model_id(self, outputs):
        with pytest.raises(
            KeyError,
            match=r"Model with ID .* not found. Provide a valid component ID\.",
        ):
            action = Action(function=action_with_no_args(), outputs=outputs)
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action._transformed_outputs

    @pytest.mark.parametrize(
        "outputs",
        [
            "",
            "component.",
            ".property",
            "component..property",
            "component.property.property",
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
    )
    def test_outputs_invalid_dot_syntax(self, outputs):
        with pytest.raises(
            ValueError,
            match=r"Invalid output format .*. Expected format is '<model_id>' or '<model_id>.<argument_name>'\.",
        ):
            action = Action(function=action_with_no_args(), outputs=outputs)
            # An error is raised when accessing _transformed_outputs which is fine because validation is then performed.
            action._transformed_outputs

    def test_outputs_invalid_missing_action_attribute(self, manager_for_testing_actions_output_input_prop):
        with pytest.raises(
            KeyError,
            match=r"Model with ID `known_model_with_no_default_props` has no `__default__` key inside its"
            r" `_action_outputs` property\. Specify the output explicitly as"
            r" `known_model_with_no_default_props.<property>`\.",
        ):
            action = Action(function=action_with_no_args(), outputs=["known_model_with_no_default_props"])
            action._transformed_outputs


class TestBaseActionUtilMethods:
    """Tests for private util functions."""

    @pytest.mark.parametrize(
        "input_value, expected_is_notification_payload",
        [
            (None, False),
            ("unknown_notification_key", False),
            ("notification_key", True),
            ((None, None), False),
            (("unknown_notification_key", None), False),
            (("notification_key", None), True),
            (("notification_key", None, None), False),
        ],
    )
    def test_is_notification_payload(self, input_value, expected_is_notification_payload):
        action = Action(function=action_with_no_args(), notifications={"notification_key": "Text"})

        result = action._is_notification_payload(value=input_value)
        assert result == expected_is_notification_payload

    @pytest.mark.parametrize(
        "input_value, expected_split_trailing_notification_payload",
        [
            (None, (None, None)),
            ((None, "unknown_notification_key"), ((None, "unknown_notification_key"), None)),
            ((None, "notification_key"), (None, "notification_key")),
            ((1, 2, 3, "notification_key"), ((1, 2, 3), "notification_key")),
            (([1, 2, 3], "notification_key"), ([1, 2, 3], "notification_key")),
        ],
    )
    def test_split_trailing_notification_payload(self, input_value, expected_split_trailing_notification_payload):
        action = Action(function=action_with_no_args(), notifications={"notification_key": "Text"})

        result = action._split_trailing_notification_payload(return_value=input_value)
        assert result == expected_split_trailing_notification_payload

    @pytest.mark.parametrize(
        "input_notification_payload, expected_notification_key, expected_notification_result",
        [
            (None, None, None),
            ("notification_key", "notification_key", None),
            (("notification_key", "notification_result"), "notification_key", "notification_result"),
        ],
    )
    def test_parse_notification_payload(
        self,
        input_notification_payload,
        expected_notification_key,
        expected_notification_result,
    ):
        action = Action(function=action_with_no_args())

        result_notification_key, result_notification_result = action._parse_notification_payload(
            notification_payload=input_notification_payload
        )

        assert result_notification_key == expected_notification_key
        assert result_notification_result == expected_notification_result

    @pytest.mark.parametrize(
        "callback_outputs, expected_no_update_outputs",
        [
            (Output("component", "property"), no_update),
            ([Output("component", "property")], [no_update]),
            (
                [
                    Output("component_1", "property"),
                    Output("component_2", "property"),
                ],
                [no_update, no_update],
            ),
            ({"component": Output("component", "property")}, {"component": no_update}),
            (
                {
                    "component_1": Output("component_1", "property"),
                    "component_2": Output("component_2", "property"),
                },
                {"component_1": no_update, "component_2": no_update},
            ),
        ],
    )
    def test_no_update_outputs(self, callback_outputs, expected_no_update_outputs):
        action = Action(function=action_with_no_args())

        result = action._no_update_outputs(outputs_spec=callback_outputs)
        assert result == expected_no_update_outputs

    @pytest.mark.parametrize("notification_key", ["unknown_notification_key", "none_notification_key"])
    def test_render_notification_no_update(self, notification_key):
        action = Action(function=action_with_no_args(), notifications={"none_notification_key": None})

        result = action._render_notification(notification_key=notification_key)
        assert result == no_update

    def test_render_notification_none(self):
        # show_notification is BaseAction that does not support the "notifications" input field or property
        action = show_notification(text="Test")

        result = action._render_notification(notification_key="success")
        assert result is None

    @pytest.mark.parametrize(
        "notification_result, error_msg, expected_rendered_notification",
        [
            (None, None, "Result: Error:"),
            ("actions_result", "actions_error", "Result:actions_result Error:actions_error"),
        ],
    )
    def test_render_notification_with_notification_result(
        self,
        notification_result,
        error_msg,
        expected_rendered_notification,
    ):
        action = Action(
            function=action_with_no_args(), notifications={"notification_key": "Result:{{result}} Error:{{error_msg}}"}
        )

        result = action._render_notification(
            notification_key="notification_key",
            notification_result=notification_result,
            error_msg=error_msg,
        )

        assert len(result) == 1

        result_notification_text = result[0]["message"].children
        assert result_notification_text == expected_rendered_notification


class TestBaseActionCallbackFunction:
    @pytest.mark.parametrize(
        "action_with_mock_return_value, callback_outputs",
        [
            # no outputs
            (None, []),
            (None, {}),
            (None, None),
            # single output - note this is not [Output(...)] in a list
            (None, Output("component", "property")),
            ("abc", Output("component", "property")),
            ("notification_key", Output("component", "property")),
            (["value_1", "value_2"], Output("component", "property")),
            (["value_1", "notification_key"], Output("component", "property")),
            ({"key_1": "value_1"}, Output("component", "property")),
            (("value_1", "unknown_notification_key"), Output("component", "property")),
            (("value_1", ("unknown_notification_key", "notification_result")), Output("component", "property")),
            # These two edge cases are the only breaking changes introduced with conditional notification feature.
            # Find more about the edge cases in the source code.
            pytest.param(("value_1", "notification_key"), Output("component", "property"), marks=pytest.mark.xfail),
            pytest.param(
                ("value_1", ("notification_key", "notification_result")),
                Output("component", "property"),
                marks=pytest.mark.xfail,
            ),
            # multiple list outputs
            ("ab", [Output("component_1", "property"), Output("component_2", "property")]),
            (["value_1", "value_2"], [Output("component_1", "property"), Output("component_2", "property")]),
            (["value_1", "notification_key"], [Output("component_1", "property"), Output("component_2", "property")]),
            (("value_1", "notification_key"), [Output("component_1", "property"), Output("component_2", "property")]),
            (
                ("value_1", ("notification_key", "notification_result")),
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                [Output("component", "property"), Output("component_2", "property")],
            ),
            # dict outputs
            ({"component_1": "value_1"}, {"component_1": Output("component", "property")}),
            (
                {"component_1": "value_1", "component_2": "value_2"},
                {"component_1": Output("component_1", "property"), "component_2": Output("component_2", "property")},
            ),
        ],
        indirect=["action_with_mock_return_value"],
    )
    def test_action_callback_function_return_value_valid(self, action_with_mock_return_value, callback_outputs):
        action = Action(function=action_with_mock_return_value(), notifications={"notification_key": "Test"})
        # If no error is raised by _action_callback_function then running it should return exactly the same
        # as the output of the action_with_mock_return_value.
        assert action._action_callback_function(inputs={}, outputs=callback_outputs) == {
            "external_return": action_with_mock_return_value()(),
            "notification_payload": None,
        }

    @pytest.mark.parametrize(
        "action_with_mock_return_value, expected_external_return, expected_notification_payload, callback_outputs",
        [
            # no outputs
            ("notification_key", None, "notification_key", None),
            (("notification_key", "notification_result"), None, ("notification_key", "notification_result"), None),
            # single output
            (("value_1", "notification_key"), "value_1", "notification_key", Output("component", "property")),
            (
                ("value_1", ("notification_key", "notification_result")),
                "value_1",
                ("notification_key", "notification_result"),
                Output("component", "property"),
            ),
            # list outputs
            (
                ("ab", "notification_key"),
                "ab",
                "notification_key",
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                ("ab", ("notification_key", "notification_result")),
                "ab",
                ("notification_key", "notification_result"),
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                (["value_1", "value_2"], "notification_key"),
                ["value_1", "value_2"],
                "notification_key",
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                (["value_1", "value_2"], ("notification_key", "notification_result")),
                ["value_1", "value_2"],
                ("notification_key", "notification_result"),
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                ("value_1", "value_2", "notification_key"),
                ("value_1", "value_2"),
                "notification_key",
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            (
                ("value_1", "value_2", ("notification_key", "notification_result")),
                ("value_1", "value_2"),
                ("notification_key", "notification_result"),
                [Output("component_1", "property"), Output("component_2", "property")],
            ),
            # dict outputs
            (
                ({"component_1": "value_1"}, "notification_key"),
                {"component_1": "value_1"},
                "notification_key",
                {"component_1": Output("component", "property")},
            ),
            (
                ({"component_1": "value_1"}, ("notification_key", "notification_result")),
                {"component_1": "value_1"},
                ("notification_key", "notification_result"),
                {"component_1": Output("component", "property")},
            ),
        ],
        indirect=["action_with_mock_return_value"],
    )
    def test_action_callback_function_return_value_and_notification_valid(
        self, action_with_mock_return_value, expected_external_return, expected_notification_payload, callback_outputs
    ):
        action = Action(function=action_with_mock_return_value(), notifications={"notification_key": "Text"})
        # If no error is raised by _action_callback_function then running it should return exactly the same
        # as the output of the action_with_mock_return_value.
        assert action._action_callback_function(inputs={}, outputs=callback_outputs) == {
            "external_return": expected_external_return,
            "notification_payload": expected_notification_payload,
        }

    @pytest.mark.parametrize("callback_outputs", [[], {}, None])
    @pytest.mark.parametrize(
        "action_with_mock_return_value", [False, 0, "", [], (), {}, "unknown_notification_key"], indirect=True
    )
    def test_action_callback_function_no_outputs_return_value_not_none(
        self, action_with_mock_return_value, callback_outputs
    ):
        action = Action(function=action_with_mock_return_value(), notifications={"notification_key": "Text"})
        with pytest.raises(
            ValueError, match=r"Action function has returned a value but the action has no defined outputs\."
        ):
            action._action_callback_function(inputs={}, outputs=callback_outputs)

    @pytest.mark.parametrize("action_with_mock_return_value", [None, False, 0, 123], indirect=True)
    def test_action_callback_function_outputs_list_return_value_not_collection(self, action_with_mock_return_value):
        # Note it's not possible for _action_callback_function to be called with a single Output in a list, like
        # [Output(...)]. This would always be done as Output(...) outside a list instead.
        action = Action(function=action_with_mock_return_value())
        with pytest.raises(
            ValueError,
            match=r"Action function has not returned a list-like object but the action's defined outputs are a list\.",
        ):
            action._action_callback_function(inputs={}, outputs=[Output("component_1", "property")])

    @pytest.mark.parametrize(
        "action_with_mock_return_value",
        [None, False, 0, 123, "", [], (), ({"output": "value_1"}, "unknown_notification_key")],
        indirect=["action_with_mock_return_value"],
    )
    def test_action_callback_function_outputs_mapping_return_value_not_mapping(self, action_with_mock_return_value):
        action = Action(function=action_with_mock_return_value(), notifications={"notification_key": "Text"})
        with pytest.raises(
            ValueError,
            match=r"Action function has not returned a dictionary-like object "
            r"but the action's defined outputs are a dictionary\.",
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})

    @pytest.mark.parametrize(
        "action_with_mock_return_value",
        ["", [], (), {}, "abc", [1, 2, 3], (1, 2, 3), {"a": 1, "b": 2, "c": 3}],
        indirect=["action_with_mock_return_value"],
    )
    def test_action_callback_function_outputs_list_return_value_length_not_match(self, action_with_mock_return_value):
        action = Action(function=action_with_mock_return_value(), notifications={"notification_key": "Text"})
        with pytest.raises(
            ValueError,
            match=r"Number of action's returned elements .+ does not match the number of action's defined outputs 2\.",
        ):
            action._action_callback_function(
                inputs={}, outputs=[Output("component_1", "property"), Output("component_2", "property")]
            )

    @pytest.mark.parametrize(
        "action_with_mock_return_value",
        [{}, {"another_output": 1}, {"output": 1, "another_output": 2}],
        indirect=["action_with_mock_return_value"],
    )
    def test_action_callback_function_outputs_mapping_return_value_keys_not_match(self, action_with_mock_return_value):
        action = Action(function=action_with_mock_return_value())
        with pytest.raises(
            ValueError,
            match=r"Keys of action's returned value .+ do not match the action's defined outputs {'output'}.",
        ):
            action._action_callback_function(inputs={}, outputs={"output": Output("component", "property")})
