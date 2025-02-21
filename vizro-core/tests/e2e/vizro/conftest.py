import os

import e2e.vizro.constants as cnst
import pytest
import yaml
from e2e.vizro.checkers import browser_console_warnings_checker
from e2e.vizro.waiters import callbacks_finish_waiter
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions


# dash_br_driver options hook
def pytest_setup_options():
    # if os.getenv("BROWSER") == "firefox":
    #     options = FFOptions()
    #     options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
    if os.getenv("BROWSER") == "chrome_mobile":
        options = ChromeOptions()
        options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
        return options


def make_teardown(dash_br):
    data = {
        "max": 7,
        "min": 6,
        "setosa": 5,
        "versicolor": 10,
        "virginica": 15,
    }
    with open("tests/e2e/vizro/dashboards/default/dynamic_filters_data.yaml", "w") as file:
        yaml.dump(data, file)
    # checking for browser console errors
    if os.getenv("BROWSER") != "firefox":
        try:
            log_levels = [level for level in dash_br.get_logs() if level["level"] == "SEVERE" or "WARNING"]
            if log_levels:
                for log_level in log_levels:
                    browser_console_warnings_checker(log_level, log_levels)
        except WebDriverException:
            pass


@pytest.fixture(autouse=True)
def dash_br_driver(dash_br, request):
    """Built-in driver from the dash library."""
    port = request.param.get("port", cnst.DEFAULT_PORT) if hasattr(request, "param") else cnst.DEFAULT_PORT
    path = request.param.get("path", "") if hasattr(request, "param") else ""
    dash_br.driver.set_window_size(1920, 1080)
    dash_br.server_url = f"http://127.0.0.1:{port}/{path}"
    return dash_br


@pytest.fixture(autouse=True)
def wait_for_callbacks(dash_br):
    callbacks_finish_waiter(dash_br)


@pytest.fixture(autouse=True)
def teardown_method(request):
    """Fixture checks log errors and quits the driver after each test."""
    yield
    for driver_name in [
        "dash_br",
        #  TODO: uncomment for the full scope of tests
        # "driver",
        # "chromedriver_second_browser",
    ]:
        if (driver := request.node.funcargs.get(driver_name)) is not None:
            make_teardown(driver)
