import os

import pytest
from e2e_waiters import (
    wait_for,
    webdriver_click_waiter,
    webdriver_waiter,
    webdriver_waiter_css,
)
from selenium.common import InvalidSelectorException, TimeoutException
from e2e_fake_data_generator import create_genre_popularity_by_country


@pytest.mark.parametrize(
    "chromedriver",
    [({"port": 8050})],
    indirect=["chromedriver"],
)
def test_chart_ui(chromedriver):
    # Create test dataset
    popularity_dataset = create_genre_popularity_by_country(start_year=1980, end_year=2023, records_per_year=10)
    # Save to a CSV file
    popularity_dataset.to_csv("tests/tests_utils/genre_popularity_by_country.csv", index=False)

    # fill in values
    api_key = webdriver_waiter(chromedriver, '//*[@id="settings-api-key"]')
    api_base = webdriver_waiter(chromedriver, '//*[@id="settings-api-base"]')
    api_key.send_keys(os.environ["OPENAI_API_KEY"])
    api_base.send_keys(os.environ["OPENAI_API_BASE"])

    # close panel
    webdriver_click_waiter(chromedriver, '//*[@class="btn-close"]')

    # upload file
    file_input = webdriver_waiter_css(chromedriver, 'input[type="file"]')
    file_input.send_keys(os.path.abspath("tests/tests_utils/genre_popularity_by_country.csv"))
    webdriver_click_waiter(chromedriver, '//*[@id="data-upload-id"]')

    # enter prompt
    prompt = webdriver_waiter(chromedriver, '//*[@id="text-area"]')
    prompt.send_keys("Create bar graph by genre")

    # choose gpt version
    webdriver_click_waiter(chromedriver, '//*[@class="Select-arrow"]')
    webdriver_waiter(chromedriver, '//*[@class="Select-menu-outer"]')
    webdriver_click_waiter(chromedriver, '//*/div[text()="gpt-4o-mini"]')

    # click run VizroAI
    webdriver_click_waiter(chromedriver, '//*[@id="trigger-button"]')

    # check result
    def _text_waiter():
        try:
            webdriver_waiter(
                chromedriver,
                '//*[starts-with(@class, "language-python")]',
            )
            return True
        except (TimeoutException, InvalidSelectorException):
            return False

    wait_for(_text_waiter)
