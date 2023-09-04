# ruff: noqa: F403, F405
import os
from pathlib import Path

import chromedriver_autoinstaller
import pytest


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
        chromedriver_autoinstaller.install()


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
