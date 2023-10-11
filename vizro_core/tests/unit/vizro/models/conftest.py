import pytest

from vizro.models.types import capture


@pytest.fixture
@capture("action")
def test_action_function():
    pass
