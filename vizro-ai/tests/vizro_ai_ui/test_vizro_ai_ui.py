import os

import pytest
from selenium.common import InvalidSelectorException, TimeoutException
from tests.helpers.common import (
    wait_for,
    webdriver_click_waiter,
    webdriver_waiter,
    webdriver_waiter_css,
)


@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader():DeprecationWarning")
@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
@pytest.mark.filterwarnings("ignore:unclosed file:ResourceWarning")
@pytest.mark.parametrize(
    "chromedriver",
    [({"port": 8050})],
    indirect=["chromedriver"],
)
def test_chart_ui(chromedriver):
    # fill in values
    api_key = webdriver_waiter(chromedriver, '//*[@id="settings-api-key"]')
    api_base = webdriver_waiter(chromedriver, '//*[@id="settings-api-base"]')
    api_key.send_keys(os.environ["OPENAI_API_KEY"])
    api_base.send_keys(os.environ["OPENAI_API_BASE"])

    # close panel
    webdriver_click_waiter(chromedriver, '//*[@class="btn-close"]')

    # upload file
    file_input = webdriver_waiter_css(chromedriver, 'input[type="file"]')
    file_input.send_keys(os.path.abspath("tests/vizro_ai_ui/genre_popularity_by_country.csv"))
    webdriver_click_waiter(chromedriver, '//*[@id="data-upload-id"]')

    # enter prompt
    prompt = webdriver_waiter(chromedriver, '//*[@id="text-area-id"]')
    prompt.send_keys("Create bar graph by genre")

    # choose gpt version
    webdriver_click_waiter(chromedriver, '//*[@class="Select-arrow"]')
    webdriver_waiter(chromedriver, '//*[@class="Select-menu-outer"]')
    webdriver_click_waiter(chromedriver, '//*/div[text()="gpt-4o-mini"]')

    # click run VizroAI
    webdriver_click_waiter(chromedriver, '//*[@id="trigger-button-id"]')

    # check result
    def _text_waiter():
        try:
            webdriver_waiter(
                chromedriver,
                '//*[starts-with(@class, "anguage-python")]',
            )
            return True
        except (TimeoutException, InvalidSelectorException):
            return False

    wait_for(_text_waiter)
