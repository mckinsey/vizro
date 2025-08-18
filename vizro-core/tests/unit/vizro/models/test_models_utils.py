import re
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.actions import export_data
from vizro.models._models_utils import warn_description_without_title


@dataclass
class MockValidationInfo:
    data: dict


class TestSharedValidators:
    @pytest.mark.parametrize(
        "captured_callable, error_message",
        [
            (
                "standard_px_chart",
                "A callable of mode `graph` has been provided. Please wrap it inside `vm.Graph(figure=...)`",
            ),
            (
                "standard_ag_grid",
                "A callable of mode `ag_grid` has been provided. Please wrap it inside `vm.AgGrid(figure=...)`",
            ),
            (
                "standard_dash_table",
                "A callable of mode `table` has been provided. Please wrap it inside `vm.Table(figure=...)`",
            ),
            (
                "standard_kpi_card",
                "A callable of mode `figure` has been provided. Please wrap it inside `vm.Figure(figure=...)`",
            ),
        ],
    )
    def test_check_captured_callable(self, model_with_layout, captured_callable, error_message, request):
        with pytest.raises(ValidationError, match=re.escape(error_message)):
            model_with_layout(title="Title", components=[request.getfixturevalue(captured_callable)])

    def test_check_for_valid_component_types(self, model_with_layout):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "'type' does not match any of the expected tags: 'ag_grid', 'button', 'card', 'container', 'figure', "
                "'graph', 'text', 'table', 'tabs'"
            ),
        ):
            model_with_layout(title="Page Title", components=[vm.Checklist()])

    def test_warns_if_description_and_no_title(self):
        info = MockValidationInfo(data={"title": ""})
        with pytest.warns(UserWarning, match="description.*title.*missing or empty"):
            warn_description_without_title("description", info)


class TestMakeActionsChain:
    def test_model_with_empty_actions(self, mock_class_model_with_actions):
        model = mock_class_model_with_actions()
        assert model.actions == []

    def test_model_with_custom_actions(self, mock_class_model_with_actions, identity_action_function):
        action = vm.Action(function=identity_action_function())

        # Assign actions to a Vizro model so that make_actions_chain can be tested
        model = mock_class_model_with_actions(actions=action)

        assert model.actions == [action]

    def test_model_with_builtin_actions(self, mock_class_model_with_actions):
        action = export_data()

        # Assign actions to a Vizro model so that make_actions_chain can be tested
        model = mock_class_model_with_actions(actions=action)

        assert model.actions == [action]

    def test_model_with_multiple_actions(self, mock_class_model_with_actions, identity_action_function):
        action_1 = vm.Action(function=identity_action_function())
        action_2 = export_data()

        # Assign actions to a Vizro model so that make_actions_chain can be tested
        model = mock_class_model_with_actions(actions=[action_1, action_2])

        assert model.actions == [action_1, action_2]

    def test_model_action_protected_attributes(self, mock_class_model_with_actions, identity_action_function):
        action_1 = vm.Action(id="action-1-id", function=identity_action_function())
        action_2 = export_data(id="action-2-id")

        # Assign actions to a Vizro model so that make_actions_chain can be tested
        mock_class_model_with_actions(id="model-id", actions=[action_1, action_2])

        assert action_1._first_in_chain is True
        assert action_2._first_in_chain is False

        assert action_1._trigger == "model-id.default_property"
        assert action_2._trigger == "action-1-id_finished.data"

        assert action_1._prevent_initial_call_of_guard is True
        assert action_2._prevent_initial_call_of_guard is True

        assert action_1._parent_model_id == "model-id"
        assert action_2._parent_model_id == "model-id"
