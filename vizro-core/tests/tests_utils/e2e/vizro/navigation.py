import time

from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_accordion_active
from e2e.vizro.paths import page_title_path, slider_handler_path, slider_value_path
from e2e.vizro.waiters import graph_load_waiter
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def click_element_by_xpath_selenium(driver, xpath):
    WebDriverWait(driver.driver, timeout=cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def hover_over_element_by_xpath_selenium(driver, xpath):
    ActionChains(driver.driver).move_to_element(driver.driver.find_element(By.XPATH, xpath)).perform()


def accordion_select(driver, accordion_name):
    """Selecting accordion and checking if it is active."""
    click_element_by_xpath_selenium(driver, f"//button[text()='{accordion_name}']")
    check_accordion_active(driver, accordion_name)
    # to let accordion open
    time.sleep(1)


def page_select(driver, page_name, graph_check=True, page_path=None):
    """Selecting page and checking if it has proper title."""
    page_path = page_path if page_path else f"/{page_name}"
    driver.multiple_click(f"a[href='{page_path}']", 1)

    driver.wait_for_contains_text(page_title_path(), page_name)
    if graph_check:
        graph_load_waiter(driver)


def page_select_selenium(driver, page_path, page_name, timeout=cnst.SELENIUM_WAITERS_TIMEOUT, graph_check=True):
    """Selecting page and checking if it has proper title for pure selenium."""
    WebDriverWait(driver, timeout).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='{page_path}']"))
    ).click()
    WebDriverWait(driver, timeout).until(
        expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, page_title_path()), page_name)
    )
    if graph_check:
        WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class='dash-graph'] path[class='xtick ticks crisp']")
            )
        )


def select_slider_handler(driver, elem_id, value, handler_class="rc-slider-handle"):
    driver.multiple_click(slider_value_path(elem_id=elem_id, value=value), 1)
    driver.multiple_click(slider_handler_path(elem_id=elem_id, handler_class=handler_class), 1)


def clear_dropdown(driver, dropdown_id):
    selected_options = driver.find_elements(f"div[id='{dropdown_id}'] span[class='Select-value-label']")
    selected_options_list = ["".join(option.text.split()) for option in selected_options]
    for option in range(0, len(selected_options_list)):
        driver.clear_input(f"div[id='{dropdown_id}']")


def select_dropdown_value(driver, dropdown_id, value):
    """Steps to select value in dropdown."""
    driver.select_dcc_dropdown(f"div[id='{dropdown_id}']", value)
