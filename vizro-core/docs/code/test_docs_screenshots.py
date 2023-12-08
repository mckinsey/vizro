import pytest
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def chromedriver(request):
    """Fixture for starting chromedriver."""
    options = Options()
    options.add_argument("--headless"),
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option(
        "prefs",
        {"download.default_directory": "."},
    )
    driver = webdriver.Chrome(options=options)
    driver.get(f"http://127.0.0.1:{request.param.get('port')}/first-page")
    return driver


@pytest.mark.parametrize(
    "chromedriver", [({"port": 5004})], indirect=["chromedriver"]
)
def test_generate_screenshots(chromedriver):
    WebDriverWait(
        chromedriver, 10, ignored_exceptions=StaleElementReferenceException
    ).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[starts-with(@class, "sc-")][contains(@class, "daq-booleanswitch--light__background")]/button')))
    WebDriverWait(
        chromedriver, 10, ignored_exceptions=StaleElementReferenceException
    ).until(expected_conditions.element_to_be_clickable(
        (By.XPATH, '//*[@class="selector_dropdown_container"]//*[@class="dash-dropdown"]'))).click()
    chromedriver.save_screenshot("first_page.png")
    full = chromedriver.get_screenshot_as_png()
    from PIL import Image
    from io import BytesIO
    im = Image.open(BytesIO(full))
    #  using https://chromewebstore.google.com/detail/pixel-measurement/jdkcdajnaldgjmkdkkkgenbgdajaaapa
    #  using https://chromewebstore.google.com/detail/resolution-test/pggmjcdagmkafagmhhaickkjnfgnhjgg
    width, height = 121*2, 129*2
    x, y = 16*2, 435*2  # left, top
    # Select area to crop
    area = (x, y, x + width, y + height)
    im = im.crop(area)
    im.save('F1-info.png')
    # elem = chromedriver.find_element(By.XPATH, '//*[@class="selector_container"]')
    # elem.screenshot(f"first_page_elem.png")

