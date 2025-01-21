import os
import runpy
from pathlib import Path

import chromedriver_autoinstaller
import pytest
from e2e_common_waiters import (
    wait_for,
    webdriver_click_waiter,
    webdriver_waiter,
    webdriver_waiter_css,
)
from fake_data_generator import create_genre_popularity_by_country
from selenium.common import InvalidSelectorException, TimeoutException
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
    example_directory = request.getfixturevalue("example_path")
    monkeypatch.chdir(example_directory)
    monkeypatch.syspath_prepend(example_directory)
    return runpy.run_path("app.py")["dashboard"]
    # Both run_path and run_module contaminate sys.modules, so we need to undo this in order to avoid interference
    # between tests. However, if you do this then importlib.import_module seems to cause the problem due to mysterious
    # reasons. The current system should work well so long as there's no sub-packages with clashing names in the
    # examples.


examples_path = Path(__file__).parents[2] / "examples"


@pytest.mark.parametrize(
    "example_path",
    [
        (examples_path / "dashboard_ui"),
    ],
    ids=str,
)
def test_chart_ui(dash_duo, example_path, dashboard):
    app = Vizro(assets_folder=example_path / "assets").build(dashboard).dash
    dash_duo.start_server(app)
    dash_duo_driver = dash_duo.driver

    # Create test dataset
    popularity_dataset = create_genre_popularity_by_country(start_year=1980, end_year=2023, records_per_year=10)
    # Save to a CSV file
    popularity_dataset.to_csv("genre_popularity_by_country.csv", index=False)

    # fill in values
    api_key = webdriver_waiter(dash_duo_driver, '//*[@id="settings-api-key"]')
    api_base = webdriver_waiter(dash_duo_driver, '//*[@id="settings-api-base"]')
    api_key.send_keys(os.environ["OPENAI_API_KEY"])
    api_base.send_keys(os.environ["OPENAI_API_BASE"])

    # close panel
    webdriver_click_waiter(dash_duo_driver, '//*[@class="btn-close"]')

    # upload file
    file_input = webdriver_waiter_css(dash_duo_driver, 'input[type="file"]')
    file_input.send_keys(os.path.abspath("genre_popularity_by_country.csv"))
    webdriver_click_waiter(dash_duo_driver, '//*[@id="data-upload"]')

    # enter prompt
    prompt = webdriver_waiter(dash_duo_driver, '//*[@id="text-area"]')
    prompt.send_keys("Create bar graph by genre")

    # choose gpt version
    webdriver_click_waiter(dash_duo_driver, '//*[@class="Select-arrow"]')
    webdriver_waiter(dash_duo_driver, '//*[@class="Select-menu-outer"]')
    webdriver_click_waiter(dash_duo_driver, '//*/div[text()="gpt-4o-mini"]')

    # click run VizroAI
    webdriver_click_waiter(dash_duo_driver, '//*[@id="trigger-button"]')

    # check result
    def _text_waiter():
        try:
            webdriver_waiter(
                dash_duo_driver,
                '//*[starts-with(@class, "language-python")]',
            )
            return True
        except (TimeoutException, InvalidSelectorException):
            return False

    wait_for(_text_waiter)

    # check console logs for errors
    assert dash_duo.get_logs() == []
