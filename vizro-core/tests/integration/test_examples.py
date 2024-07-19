# ruff: noqa: F403, F405
import os
import runpy
import sys
from pathlib import Path

import chromedriver_autoinstaller
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
        chromedriver_autoinstaller.install()


@pytest.fixture
def dashboard(request, monkeypatch):
    example_directory = request.getfixturevalue("example_path") / request.getfixturevalue("version")
    monkeypatch.chdir(example_directory)
    monkeypatch.syspath_prepend(example_directory)
    old_sys_modules = set(sys.modules)
    yield runpy.run_path("app.py")["dashboard"]
    # Both run_path and run_module contaminate sys.modules, so we need to undo this in order to avoid interference
    # between tests.
    for key in set(sys.modules) - old_sys_modules:
        del sys.modules[key]


examples_path = Path(__file__).parents[2] / "examples"


# Ignore deprecation warning until this is solved: https://github.com/plotly/dash/issues/2590
# The `features` examples do add_type, which ideally we would clean up afterwards to restore vizro.models to its
# previous state. Since we don't currently do this, `hatch run test` fails.
# This is difficult to fix fully by un-importing vizro.models though, since we use `import vizro.models as vm` - see
# https://stackoverflow.com/questions/437589/how-do-i-unload-reload-a-python-module.
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
# Ignore as it doesn't affect the test run
@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
@pytest.mark.parametrize(
    "example_path, version",
    [
        (examples_path / "scratch_dev", ""),
        (examples_path / "scratch_dev", "yaml_version"),
        (examples_path / "dev", ""),
        (examples_path / "dev", "yaml_version"),
        (examples_path / "_chart-gallery", ""),
        (examples_path / "kpi", ""),
    ],
    ids=str,
)
def test_dashboard(dash_duo, example_path, dashboard, version):
    app = Vizro(assets_folder=example_path / "assets").build(dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
