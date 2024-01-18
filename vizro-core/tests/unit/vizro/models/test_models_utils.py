import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture(params=[vm.Container, vm.Page])
def model_with_components(request):
    return request.param


class TestSharedValidators:
    def test_set_components_validator(self, model_with_components):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            model_with_components(title="Title", components=[])

    def test_check_for_valid_component_types(self, model_with_components):
        with pytest.raises(
            ValidationError, match=re.escape("(allowed values: 'button', 'card', 'container', 'graph', 'table')")
        ):
            model_with_components(title="Page Title", components=[vm.Checklist()])
