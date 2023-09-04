import pytest

from vizro.managers import data_manager, model_manager


@pytest.fixture(autouse=True)
def reset_managers():
    yield
    model_manager._reset()
    data_manager._reset()
