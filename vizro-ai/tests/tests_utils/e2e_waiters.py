import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from e2e_constants import TIMEOUT


def wait_for(condition_function, *args):
    """Function wait for any condition to be True."""
    start_time = time.time()
    while time.time() < start_time + 10:
        if condition_function(*args):
            return True
        else:
            time.sleep(0.1)
    raise Exception(f"Timeout waiting for {condition_function.__name__}")


def webdriver_click_waiter(browserdriver, xpath):
    WebDriverWait(browserdriver, TIMEOUT, ignored_exceptions=StaleElementReferenceException).until(
        expected_conditions.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def webdriver_waiter(browserdriver, xpath):
    elem = WebDriverWait(browserdriver, TIMEOUT, ignored_exceptions=StaleElementReferenceException).until(
        expected_conditions.presence_of_element_located((By.XPATH, xpath))
    )
    return elem


def webdriver_waiter_css(browserdriver, xpath):
    elem = WebDriverWait(browserdriver, TIMEOUT, ignored_exceptions=StaleElementReferenceException).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, xpath))
    )
    return elem
