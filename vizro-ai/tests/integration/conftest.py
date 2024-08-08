import pytest
from vizro import Vizro


@pytest.fixture(autouse=True)
def reset_managers():
    # this ensures that the managers are reset before and after each test
    # the reset BEFORE all tests is important because at pytest test collection, fixtures are evaluated and hence
    # the model_manager may be populated with models from other tests
    Vizro._reset()
    yield
    Vizro._reset()
