# ruff: noqa: F403, F405
import os
from pathlib import Path

import chromedriver_autoinstaller_fix
import pytest

from vizro import Vizro


# Use monkeypatch as a session-scoped fixture.
# Taken from https://github.com/pytest-dev/pytest/issues/363#issuecomment-1335631998.
@pytest.fixture(scope="session")
def monkeypatch_session():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="session", autouse=True)
def setup_integration_test_environment(monkeypatch_session):
    # Dash debug mode seems to interfere with the tests, so we disable it here. Note "false" as a string is correct.
    monkeypatch_session.setenv("DASH_DEBUG", "false")
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller_fix.install()


@pytest.fixture
def default_dashboard(monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / "examples/default")
    monkeypatch.syspath_prepend(Path.cwd())
    from app import dashboard

    return dashboard


@pytest.fixture
def dict_dashboard(monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / "examples/from_dict")
    monkeypatch.syspath_prepend(Path.cwd())
    from app import dashboard

    return dashboard


@pytest.fixture
def json_dashboard(monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / "examples/from_json")
    monkeypatch.syspath_prepend(Path.cwd())
    from app import dashboard

    return dashboard


@pytest.fixture
def yaml_dashboard(monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / "examples/from_yaml")
    monkeypatch.syspath_prepend(Path.cwd())
    from app import dashboard

    return dashboard


def test_default_dashboard(dash_duo, default_dashboard):
    """Test if default example dashboard starts and has no errors in logs."""
    app = Vizro().build(default_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_dict_dashboard(dash_duo, dict_dashboard):
    """Test if dictionary example dashboard starts and has no errors in logs."""
    app = Vizro().build(dict_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_json_dashboard(dash_duo, json_dashboard):
    """Test if json example dashboard starts and has no errors in logs."""
    app = Vizro().build(json_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_yaml_dashboard(dash_duo, yaml_dashboard):
    """Test if yaml example dashboard starts and has no errors in logs."""
    app = Vizro().build(yaml_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
