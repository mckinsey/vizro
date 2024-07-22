import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestSharedValidators:
    def test_validate_min_length(self, model_with_layout):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            model_with_layout(title="Title", components=[])

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
                "(allowed values: 'ag_grid', 'button', 'card', 'container', 'figure', 'graph', 'table', 'tabs')"
            ),
        ):
            model_with_layout(title="Page Title", components=[vm.Checklist()])
