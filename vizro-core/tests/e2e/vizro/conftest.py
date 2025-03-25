import os

import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import browser_console_warnings_checker
from e2e.vizro.waiters import callbacks_finish_waiter
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions


# dash_br_driver options hook
def pytest_setup_options():
    if os.getenv("BROWSER") == "chrome_mobile":
        options = ChromeOptions()
        options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 14 Pro Max"})
        return options


@pytest.fixture(autouse=True)
def dash_br_driver(dash_br, request):
    """Built-in driver from the dash library."""
    port = request.param.get("port", cnst.DEFAULT_PORT) if hasattr(request, "param") else cnst.DEFAULT_PORT
    path = request.param.get("path", "") if hasattr(request, "param") else ""
    dash_br.driver.set_window_size(1920, 1080)
    dash_br.server_url = f"http://127.0.0.1:{port}/{path}"
    return dash_br


@pytest.fixture()
def chrome_driver(request):
    """Pure chromedriver."""
    options = ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    port = request.param.get("port", cnst.DEFAULT_PORT) if hasattr(request, "param") else cnst.DEFAULT_PORT
    path = request.param.get("path", "") if hasattr(request, "param") else ""
    driver.set_window_size(1920, 1080)
    driver.get(f"http://127.0.0.1:{port}/{path}")
    return driver


@pytest.fixture(autouse=True)
def wait_for_callbacks(dash_br):
    callbacks_finish_waiter(dash_br)


@pytest.fixture(autouse=True)
def teardown_method(dash_br):
    """Fixture checks log errors and quits the driver after each test."""
    yield
    # checking for browser console errors
    if os.getenv("BROWSER") in ["chrome", "chrome_mobile"]:
        try:
            error_logs = [log for log in dash_br.get_logs() if log["level"] == "SEVERE" or "WARNING"]
            for log in error_logs:
                browser_console_warnings_checker(log, error_logs)
        except WebDriverException:
            pass
