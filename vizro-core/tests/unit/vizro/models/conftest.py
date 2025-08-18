from typing import Literal

import pytest
from pydantic import model_validator

import vizro.models as vm
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import ActionsType, _IdProperty, capture


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
def mock_class_model_with_actions():
    class MockModelWithActions(vm.VizroBaseModel):
        type: Literal["mock_model_with_actions"] = "mock_model_with_actions"

        actions: ActionsType = []

        @model_validator(mode="after")
        def _make_actions_chain(self):
            return make_actions_chain(self)

        @property
        def _action_triggers(self) -> dict[str, _IdProperty]:
            return {"__default__": f"{self.id}.default_property"}

    # Add to circumvent the PydanticUserError: `MockModelWithActions` is not fully defined; call `model_rebuild()`.
    vm.Page.add_type("components", MockModelWithActions)

    return MockModelWithActions
