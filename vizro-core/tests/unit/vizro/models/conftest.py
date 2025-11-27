from typing import Literal

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


@pytest.fixture
def mock_control_wrapper_class():
    class MockControlWrapper(vm.VizroBaseModel):
        """Wrapper model around the control."""

        type: Literal["mock_control_wrapper"] = "mock_control_wrapper"
        control: vm.Filter | vm.Parameter = None

        def __new__(cls, *args, **kwargs):
            vm.Page.add_type("controls", cls)
            vm.Container.add_type("controls", cls)
            return super().__new__(cls)

        def build(self):
            return self.control.build()

    return MockControlWrapper
