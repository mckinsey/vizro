from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tests.helpers.checkers import browser_console_warnings_checker


@pytest.fixture()
def chromedriver(request):
    """Fixture for starting chromedriver."""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-search-engine-choice-screen")
    driver = webdriver.Chrome(options=options)
    driver.get(f"http://127.0.0.1:{request.param.get('port')}/")
    return driver


@pytest.fixture(autouse=True)
def teardown_method(chromedriver):
    """Fixture checks log errors and quits the driver after each test."""
    yield
    log_levels = [level for level in chromedriver.get_log("browser") if level["level"] == "SEVERE" or "WARNING"]
    if log_levels:
        for log_level in log_levels:
            browser_console_warnings_checker(log_level, log_levels)
    chromedriver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function", autouse=True)
def test_failed_check(request):
    yield
    if request.node.rep_setup.failed:
        return "setting up a test failed!", request.node.nodeid
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            driver = request.node.funcargs["chromedriver"]
            take_screenshot(driver, request.node.nodeid)
            return "executing test failed", request.node.nodeid


def take_screenshot(driver, nodeid):
    file_name = f'{nodeid}_{datetime.today().strftime("%Y-%m-%d_%H-%M")}.png'.replace("/", "_").replace("::", "__")
    driver.save_screenshot(file_name)
