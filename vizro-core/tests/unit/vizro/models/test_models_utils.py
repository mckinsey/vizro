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

    def test_validate_components_type(self, model_with_layout, standard_px_chart):
        with pytest.raises(
            ValidationError,
            match="A callable of mode `graph` has been provided. " "Please wrap it inside the `vm.Graph(figure=...)`.",
        ):
            model_with_layout(title="Title", components=[standard_px_chart])

    def test_check_for_valid_component_types(self, model_with_layout):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "(allowed values: 'ag_grid', 'button', 'card', 'container', 'figure', 'graph', 'table', 'tabs')"
            ),
        ):
            model_with_layout(title="Page Title", components=[vm.Checklist()])
