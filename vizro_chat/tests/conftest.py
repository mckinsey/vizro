"""Shared test fixtures."""

import pytest
from vizro import Vizro
from dash.testing.application_runners import DashDuo


@pytest.fixture(autouse=True)
def reset_vizro():
    """Reset Vizro state before each test."""
    Vizro._reset()
    yield


@pytest.fixture
def dash_duo():
    """Create a DashDuo instance for integration testing."""
    with DashDuo() as dd:
        yield dd
