import os
import runpy
from pathlib import Path

import chromedriver_autoinstaller
import pytest
from fake_data_generator import create_genre_popularity_by_country
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
def dashboard(monkeypatch):
    example_directory = Path(__file__).parents[2] / "examples/dashboard_ui"
    monkeypatch.chdir(example_directory)
    monkeypatch.syspath_prepend(example_directory)
    return runpy.run_path("app.py")["dashboard"]
    # Both run_path and run_module contaminate sys.modules, so we need to undo this in order to avoid interference
    # between tests. However, if you do this then importlib.import_module seems to cause the problem due to mysterious
    # reasons. The current system should work well so long as there's no sub-packages with clashing names in the
    # examples.


@pytest.fixture
def fake_data():
    popularity_dataset = create_genre_popularity_by_country()
    popularity_dataset.to_csv("genre_popularity_by_country.csv", index=False)
    yield os.path.abspath("genre_popularity_by_country.csv")


def test_chart_ui(dash_duo, dashboard, fake_data):
    app = Vizro(assets_folder=Path(__file__).parents[2] / "examples/dashboard_ui/assets").build(dashboard).dash
    dash_duo.start_server(app)

    # fill in values
    api_key = dash_duo.wait_for_element("#settings-api-key")
    api_base = dash_duo.wait_for_element("#settings-api-base")
    api_key.send_keys(os.environ["OPENAI_API_KEY"])
    api_base.send_keys(os.environ["OPENAI_API_BASE"])

    # close panel
    dash_duo.multiple_click(".btn-close", 1)

    # upload file
    file_input = dash_duo.wait_for_element('input[type="file"]')
    file_input.send_keys(fake_data)
    dash_duo.multiple_click("#data-upload", 1)

    # enter prompt
    prompt = dash_duo.wait_for_element("#text-area")
    prompt.send_keys("Create bar graph by genre")

    # click run VizroAI
    dash_duo.multiple_click("#trigger-button", 1)

    # check result
    dash_duo.wait_for_element(".language-python")
    dash_duo.wait_for_contains_text("span[class='hljs-keyword']", "import")

    # check console logs for errors
    assert dash_duo.get_logs() == []
