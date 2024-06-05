import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestSharedValidators:
    def test_set_components_validator(self, model_with_layout):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            model_with_layout(title="Title", components=[])

    def test_check_for_valid_component_types(self, model_with_layout):
        with pytest.raises(
            ValidationError,
            match=re.escape(
                "(allowed values: 'ag_grid', 'button', 'card', 'container', 'figure', 'graph', 'table', 'tabs')"
            ),
        ):
            model_with_layout(title="Page Title", components=[vm.Checklist()])
