"""Fixtures to be shared across several tests."""

import pytest


@pytest.fixture()
def pages_as_list():
    return ["Page 1", "Page 2"]


@pytest.fixture
def pages_as_dict():
    return {"Group": ["Page 1", "Page 2"]}
