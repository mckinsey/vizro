# ruff: noqa: F403, F405
import runpy
from pathlib import Path

import pytest

from vizro import Vizro


@pytest.fixture(params=["default", "yaml_version"])
def features_dashboard(request, monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / f"examples/features/{request.param}")
    app = runpy.run_path("app.py")
    return app["dashboard"]


# Ignore deprecation warning until this is solved: https://github.com/plotly/dash/issues/2590
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_features_dashboard(dash_duo, features_dashboard):
    app = Vizro(assets_folder=Path(__file__).parents[2] / "examples/features/assets").build(features_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
