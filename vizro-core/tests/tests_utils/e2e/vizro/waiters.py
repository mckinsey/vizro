from dash.testing.wait import until
from e2e.vizro import constants as cnst
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def graph_load_waiter(driver, graph_id):
    """Waiting for graph's x-axis to appear."""
    driver.wait_for_element(f"div[id='{graph_id}'] path[class='xtick ticks crisp']")


def graph_load_waiter_selenium(driver, graph_id, timeout=cnst.SELENIUM_WAITERS_TIMEOUT):
    """Waiting for graph's x-axis to appear for pure selenium."""
    WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, f"div[id='{graph_id}'] path[class='xtick ticks crisp']")
        )
    )


def callbacks_finish_waiter(driver):
    until(driver._wait_for_callbacks, timeout=40, poll=0.3)
