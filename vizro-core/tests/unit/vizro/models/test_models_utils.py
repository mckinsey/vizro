import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


@pytest.mark.parametrize("Model", [vm.Container, vm.Page])
class TestReusedValidators:
    def test_set_components_validator(self, Model):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            Model(title="Title", components=[])

    def test_set_layout_valid(self, Model):
        Model(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self, Model):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            Model(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_check_for_valid_component_types(self):
        with pytest.raises(
            ValidationError,
            match=re.escape("(allowed values: 'button', 'card', 'graph', 'table', 'container')"),
        ):
            vm.Page(title="Page Title", components=[vm.Checklist()])
