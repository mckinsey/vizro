import time

from e2e.vizro.checkers import check_accordion_active
from e2e.vizro.paths import page_title_path, slider_handler_path, slider_value_path
from e2e.vizro.waiters import graph_load_waiter


def accordion_select(driver, accordion_name, accordion_number):
    """Selecting accordion and checking if it is active."""
    driver.multiple_click(f"div[class='accordion accordion'] div:nth-of-type({accordion_number})", 1)
    check_accordion_active(driver, accordion_name)
    # to let accordion open
    time.sleep(1)


def page_select(driver, page_path, page_name, graph_id=None):
    """Selecting page and checking if it has proper title."""
    driver.wait_for_page()
    driver.multiple_click(f"a[href='{page_path}']", 1)
    driver.wait_for_text_to_equal(page_title_path(), page_name)
    if graph_id:
        graph_load_waiter(driver, graph_id)


def select_dropdown_value(driver, value):
    """Steps to select value in dropdown."""
    driver.multiple_click(".Select-clear", 1)
    driver.multiple_click(".Select-arrow", 1)
    driver.multiple_click(f".ReactVirtualized__Grid__innerScrollContainer div:nth-of-type({value})", 1)


def select_slider_handler(driver, elem_id, value, handler_class="rc-slider-handle"):
    driver.multiple_click(slider_value_path(elem_id=elem_id, value=value), 1)
    driver.multiple_click(slider_handler_path(elem_id=elem_id, handler_class=handler_class), 1)
