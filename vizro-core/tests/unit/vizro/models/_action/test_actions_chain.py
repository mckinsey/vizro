"""Unit tests for vizro.models.ActionChain."""

from dataclasses import dataclass

import pytest

from vizro.models._action._action import Action
from vizro.models._action._actions_chain import ActionsChain, Trigger, _set_actions
from vizro.models.types import CapturedCallable


@pytest.fixture
def test_trigger():
    return Trigger("component_id", "value")


@pytest.fixture
def test_action(identity_action_function):
    return Action(function=identity_action_function())


@pytest.fixture
def validation_info():
    @dataclass
    class MockValidationInfo:
        data: dict

    validation_info = MockValidationInfo(data={"id": "component_id"})
    return validation_info


class TestActionsChainInstantiation:
    """Tests model instantiation."""

    def test_create_actions_chain_mandatory_only(self, test_trigger):
        actions_chain = ActionsChain(trigger=test_trigger)

        assert hasattr(actions_chain, "id")
        assert actions_chain.trigger == test_trigger
        assert actions_chain.actions == []

    def test_create_action_chains_mandatory_and_optional(self, test_trigger, test_action):
        actions_chain = ActionsChain(id="actions_chain_id", trigger=test_trigger, actions=[test_action])

        assert actions_chain.id == "actions_chain_id"
        assert actions_chain.trigger == test_trigger
        assert isinstance(actions_chain.actions, list)
        assert actions_chain.actions[0] == test_action


def test_set_actions(test_action, validation_info):
    result = _set_actions(actions=[test_action], info=validation_info, trigger_property="value")
    actions_chain = result[0]
    action = actions_chain.actions[0]

    assert len(result) == 1
    assert isinstance(actions_chain, ActionsChain)
    assert actions_chain.trigger.component_property == "value"
    assert isinstance(action, Action)
    assert isinstance(action.function, CapturedCallable)
    assert action.inputs == []
    assert action.outputs == []
