import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import browser_console_warnings_checker
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions


# dash_br_driver options hook
def pytest_setup_options():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    return options


def make_teardown(dash_br):
    # checking for browser console errors
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
    dash_br.server_url = f"http://127.0.0.1:{port}/{path}"


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
