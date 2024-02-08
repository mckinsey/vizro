import pytest

import vizro.models as vm
from vizro.models.types import capture


@pytest.fixture
def identity_action_function():
    @capture("action")
    def _identity_action_function(arg=None):
        return arg

    return _identity_action_function


@pytest.fixture(params=[vm.Container, vm.Page])
def model_with_layout(request):
    return request.param
