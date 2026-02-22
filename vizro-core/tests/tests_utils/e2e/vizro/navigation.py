import time

from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_accordion_active
from e2e.vizro.paths import (
    dropdown_deselect_all_path,
    dropdown_id_path,
    dropdown_select_all_path,
    page_title_path,
)
from e2e.vizro.waiters import graph_load_waiter
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def click_element_by_xpath_selenium(driver, xpath):
    WebDriverWait(driver, timeout=cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def hover_over_element_by_xpath_selenium(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element(element).perform()


def hover_over_element_by_css_selector_selenium(driver, css_selector):
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    ActionChains(driver).move_to_element(element).perform()


def hover_over_and_click_by_css_selector_selenium(driver, css_selector):
    element = driver.find_element(By.CSS_SELECTOR, css_selector)
    ActionChains(driver).move_to_element(element).click().perform()


def modifier_click(dash_br, selector, key):
    """Clicking an element while holding a modifier key (like Shift or Ctrl)."""
    element = dash_br.find_element(selector)
    ActionChains(dash_br.driver).key_down(key).click(element).key_up(key).perform()


def accordion_select(driver, accordion_name):
    """Selecting accordion and checking if it is active."""
    click_element_by_xpath_selenium(driver.driver, f"//button[text()='{accordion_name}']")
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


def select_slider_value(driver, elem_id, value):
    slider_values = driver.find_elements(f"div[id='{elem_id}'] div div")
    for slider_value in slider_values:
        if slider_value.text == value:
            driver.click_at_coord_fractions(slider_value, fx=0, fy=0)


def clear_dropdown(driver, dropdown_id):
    driver.multiple_click(f"{dropdown_id_path(dropdown_id)} .dash-dropdown-clear", 1)


def select_dropdown_value(driver, dropdown_id, value):
    """Steps to select value in dropdown."""
    # if dropdown is open, close it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='true']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.select_dcc_dropdown(dropdown_id_path(dropdown_id), value)


def select_dropdown_select_all(driver, dropdown_id):
    """Steps to select Select All value in dropdown."""
    # if dropdown is closed, open it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='false']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.multiple_click(dropdown_select_all_path(dropdown_id), 1)


def select_dropdown_deselect_all(driver, dropdown_id):
    """Steps to select Deselect All value in dropdown."""
    # if dropdown is open, close it to avoid errors with selecting value
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='false']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    driver.multiple_click(dropdown_deselect_all_path(dropdown_id), 1)
