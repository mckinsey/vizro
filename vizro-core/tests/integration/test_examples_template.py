# ruff: noqa: F403, F405
import runpy
from pathlib import Path

import pytest

from vizro import Vizro


def template_dashboard(monkeypatch):
    monkeypatch.chdir(Path(__file__).parents[2] / "examples/template")
    app = runpy.run_path("app.py")
    return app["dashboard"]


# Ignore deprecation warning until this is solved: https://github.com/plotly/dash/issues/2590
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_template_dashboard(dash_duo, template_dashboard):
    app = Vizro(assets_folder=Path(__file__).parents[2] / "examples/template/assets").build(template_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
