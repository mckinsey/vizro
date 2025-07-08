import re
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

import vizro.models as vm
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


class TestWarnDescriptionWithoutTitle:
    @pytest.mark.parametrize(
        "model_type,title_field",
        [
            ("dashboard", "title"),
            ("page", "title"),
            ("container", "title"),
            ("tabs", "title"),
            ("graph", "title"),
            ("table", "title"),
            ("ag_grid", "title"),
            ("dropdown", "title"),
            ("radio_items", "title"),
            ("checklist", "title"),
            ("slider", "title"),
            ("range_slider", "title"),
            ("date_picker", "title"),
            ("user_input", "title"),
            ("text_area", "title"),
            ("button", "text"),
        ],
    )
    def test_warns_if_description_and_no_title_field(self, model_type, title_field):
        info = MockValidationInfo(data={title_field: "", "type": model_type})
        with pytest.warns(UserWarning, match=f"description.*{title_field}.*missing or empty"):
            warn_description_without_title("description", info)
