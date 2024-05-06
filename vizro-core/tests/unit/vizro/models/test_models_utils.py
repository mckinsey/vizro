import re

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm
from vizro.models._models_utils import _clean_path


class TestSharedValidators:
    def test_set_components_validator(self, model_with_layout):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            model_with_layout(title="Title", components=[])

    def test_check_for_valid_component_types(self, model_with_layout):
        with pytest.raises(
            ValidationError,
            match=re.escape("(allowed values: 'ag_grid', 'button', 'card', 'container', 'graph', 'table', 'tabs')"),
        ):
            model_with_layout(title="Page Title", components=[vm.Checklist()])


@pytest.mark.parametrize("enable_url", [True, False])
@pytest.mark.parametrize(
    "test_string, expected",
    [
        ("Title", "title"),
        ("Page Title", "page-title"),
        ("Page Title!", "page-title"),
        ("Another123Title", "another123title"),
        ("Some_Example%Title", "some_exampletitle"),
        ("!@#$%^&*()_+=", "_"),
        ("", ""),
    ],
)
def test_clean_path_with_url_enabled(test_string, expected, enable_url):
    cleaned_string = _clean_path(path=test_string, allowed_characters="-_/", enable_url=enable_url)
    expected_output = f"/{expected}" if enable_url else expected
    assert cleaned_string == expected_output
