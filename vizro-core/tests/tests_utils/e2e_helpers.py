from e2e_paths import graph_xaxis_tick_path
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def webdriver_click_waiter(driver, xpath):
    WebDriverWait(driver, 10, ignored_exceptions=StaleElementReferenceException).until(
        expected_conditions.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def webdriver_waiter(driver, xpath):
    elem = WebDriverWait(driver, 30, ignored_exceptions=StaleElementReferenceException).until(
        expected_conditions.presence_of_element_located((By.XPATH, xpath))
    )
    return elem


def graph_load_waiter(driver, graph_id):
    webdriver_waiter(driver, graph_xaxis_tick_path(graph_id))
