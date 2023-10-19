import pytest

from vizro import Vizro


@pytest.fixture(autouse=True)
def reset_managers():
    # this ensures that the managers are reset before and after each test
    # in principle clearing after every test should suffice, but this serves as a safety measure
    # there are two tests in `test_get_action_loop_components.py` that fail without this
    Vizro._clear_state()
    yield
    Vizro._clear_state()


@pytest.fixture()
def vizro_app():
    """Fixture to instantiate Vizro/Dash app. Required when needing to register pages."""
    yield Vizro()
