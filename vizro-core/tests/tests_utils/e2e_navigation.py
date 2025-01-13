import time

from e2e_helpers import webdriver_click_waiter, webdriver_waiter, graph_load_waiter
from e2e_paths import page_accordion_path, page_title_path, accordion_path


def accordion_select(chromdriver, accordion_name):
    webdriver_click_waiter(chromdriver, accordion_path(accordion_name))
    webdriver_waiter(
        chromdriver, f'//*{accordion_path(accordion_name)}[@aria-expanded="true"]'
    )


def page_select(driver, page_name, graph_id=None, accordion_name=None):
    if accordion_name:
        # choose accordion
        accordion_select(driver, accordion_name=accordion_name.upper())
    time.sleep(1)  # to let accordion open
    webdriver_click_waiter(driver, page_accordion_path(page_name))
    webdriver_waiter(driver, page_title_path(page_name))
    if graph_id:
        graph_load_waiter(driver, graph_id)
