"""Fixtures to be shared across several tests."""

import pytest

import vizro.models as vm
from vizro.actions import filter_interaction


@pytest.fixture
def filter_interaction_action():
    return vm.Action(function=filter_interaction())
