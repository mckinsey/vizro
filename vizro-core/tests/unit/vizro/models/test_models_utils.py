import re
import numpy as np
import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
from vizro.models._components.form import Form
from vizro.models._models_utils import get_unique_grid_component_ids


@pytest.mark.parametrize("grid", [[[0, -1], [1, 2]], [[0, -1, 1, 2]], [[-1, -1, -1], [0, 1, 2]]])
def test_get_unique_grid_component_ids(grid):
    result = get_unique_grid_component_ids(grid)
    expected = np.array([0, 1, 2])

    assert isinstance(result, np.ndarray)
    assert (result == expected).all()


# TODO: Add vm.Form here as soon as it is implemented
@pytest.mark.parametrize("Model", [vm.Container, vm.Page, Form])
class TestReusedValidators:
    def test_set_components_validator(self, Model):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            Model(title="Title", components=[])

    def test_set_layout_valid(self, Model):
        Model(title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    def test_set_layout_invalid(self, Model):
        with pytest.raises(ValidationError, match="Number of page and grid components need to be the same."):
            Model(title="Title", components=[vm.Button()], layout=vm.Layout(grid=[[0, 1]]))

    @pytest.mark.parametrize("Model", [vm.Container, vm.Page])
    def test_check_for_valid_component_types(self, Model):
        with pytest.raises(ValidationError,match=re.escape("(allowed values: 'button', 'card', 'container', 'graph', 'table')")):
            Model(title="Page Title", components=[vm.Checklist()])

    def test_check_for_valid_form_component_types(self):
        with pytest.raises(ValidationError,
                           match=re.escape("(allowed values: 'button', 'card', 'container', 'graph', 'table')")):
            Form(title="Page Title", components=[vm.Card("""Text""")])
