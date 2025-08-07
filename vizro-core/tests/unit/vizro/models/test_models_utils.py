import re
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.actions import export_data
from vizro.models._models_utils import coerce_actions_type, warn_description_without_title


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

    @pytest.mark.parametrize(
        "actions_input",
        [
            vm.Action(function=export_data()),  # Single action
            [vm.Action(function=export_data())],  # List of actions
        ],
    )
    def test_coerce_actions_type(self, actions_input):
        """Test that coerce_actions_type always returns the expected list format."""
        result = coerce_actions_type(actions_input)

        expected = actions_input if isinstance(actions_input, list) else [actions_input]
        assert result == expected

    def test_coerce_actions_type_integration(self):
        """Test that single actions work with actual components."""
        action = export_data()
        button = vm.Button(actions=action)
        assert button.actions == [action]
