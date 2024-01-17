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


@pytest.mark.parametrize("dir", ["_dev", "demo", "features"])
@pytest.fixture(params=["/", "/yaml_version"])
def dashboard(request, dir, monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / f"examples/{dir}/{request.param}")
    app = runpy.run_path("app.py")
    return app["dashboard"]


# Ignore deprecation warning until this is solved: https://github.com/plotly/dash/issues/2590
@pytest.mark.parametrize("dir", ["_dev", "demo", "features"])
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_dashboard(dash_duo, dir, dashboard):
    app = Vizro(assets_folder=Path(__file__).parents[2] / f"examples/{dir}/assets").build(dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
