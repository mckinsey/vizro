"""Shared test fixtures."""

import pytest
from vizro import Vizro


@pytest.fixture(autouse=True)
def reset_vizro():
    """Reset Vizro state before each test."""
    Vizro._reset()
    yield
