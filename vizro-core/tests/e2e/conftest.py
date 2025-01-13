from datetime import datetime

import pytest
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from e2e_checkers import browser_console_warnings_checker
import e2e_constants as cnst

# functions


# dash_br_driver options hook
def pytest_setup_options():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    return options


def make_teardown(driver):
    # checking for browser console errors
    try:
        log_levels = [
            level
            for level in driver.get_log("browser")
            if level["level"] == "SEVERE" or "WARNING"
        ]
        if log_levels:
            for log_level in log_levels:
                browser_console_warnings_checker(log_level, log_levels)
    except WebDriverException:
        pass
    driver.quit()


# make a screenshot with a name of the test, date and time
def take_screenshot(driver, nodeid):
    file_name = (
        f'{nodeid}_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S-%f")}.png'.replace(
            "/", "_"
        ).replace("::", "__")
    )
    driver.save_screenshot(file_name)


# drivers


@pytest.fixture(autouse=True)
def dash_br_driver(dash_br, request):
    """Built-in driver from the dash library."""
    port = request.param.get("port", cnst.DEFAULT_PORT) if hasattr(request, "param") else cnst.DEFAULT_PORT
    path = request.param.get("path", "") if hasattr(request, "param") else ""
    dash_br.server_url = f"http://127.0.0.1:{port}/{path}"
    return dash_br.driver


# teardowns


@pytest.fixture(autouse=True)
def teardown_method(request):
    """Fixture checks log errors and quits the driver after each test."""
    yield
    for driver_name in [
        "dash_br_driver",
        #  TODO: uncomment for the full scope of tests
        # "driver",
        # "chromedriver_second_browser",
    ]:
        if (driver := request.node.funcargs.get(driver_name)) is not None:
            make_teardown(driver)


# failed screenshots logic


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


# check if a test has failed
@pytest.fixture(scope="function", autouse=True)
def test_failed_check(request):
    yield
    # request.node is an "item" because we use the default
    # "function" scope
    if request.node.rep_setup.failed:
        return "setting up a test failed!", request.node.nodeid
    elif request.node.rep_setup.passed and request.node.rep_call.failed:
        dash_br_driver = request.node.funcargs.get("dash_br_driver")
        take_screenshot(dash_br_driver, request.node.nodeid)
        #  TODO: uncomment for the full scope of tests
        # driver = request.node.funcargs.get("driver")
        # chromedriver_second_browser = request.node.funcargs.get(
        #     "chromedriver_second_browser"
        # )
        # if dash_br_driver is not None and driver is None:
        #     take_screenshot(dash_br_driver, request.node.nodeid)
        # if dash_br_driver and driver is not None:
        #     take_screenshot(driver, request.node.nodeid)
        # if driver and chromedriver_second_browser is not None:
        #     take_screenshot(chromedriver_second_browser, request.node.nodeid)
        return "executing test failed", request.node.nodeid
