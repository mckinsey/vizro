# ruff: noqa: F403, F405
import os
import runpy
from pathlib import Path

import chromedriver_autoinstaller_fix
import pytest
from vizro import Vizro


# Taken from https://github.com/pytest-dev/pytest/issues/363#issuecomment-1335631998.
@pytest.fixture(scope="module")
def monkeypatch_session():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module", autouse=True)
def setup_integration_test_environment(monkeypatch_session):
    # Dash debug mode seems to interfere with the tests, so we disable it here. Note "false" as a string is correct.
    monkeypatch_session.setenv("DASH_DEBUG", "false")
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller_fix.install()


@pytest.fixture
def dashboard(request, monkeypatch):
    monkeypatch.chdir(request.getfixturevalue("example_path") / request.getfixturevalue("version"))
    app = runpy.run_path("app.py")
    return app["dashboard"]


examples_path = Path(__file__).parents[2] / "examples"


# Ignore deprecation warning until this is solved: https://github.com/plotly/dash/issues/2590
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
@pytest.mark.parametrize(
    "example_path, version",
    [
        (examples_path / "_dev", ""),
        (examples_path / "features", ""),
        (examples_path / "demo", ""),
        (examples_path / "_dev", "yaml_version"),
        (examples_path / "features", "yaml_version"),
    ],
)
def test_dashboard(dash_duo, example_path, dashboard, version):
    app = Vizro(assets_folder=example_path / "assets").build(dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
