import e2e.constants as cnst
from e2e.checkers import check_text
from e2e.helpers import webdriver_click_waiter, webdriver_waiter
from e2e.paths import href_path, nav_card_text_path


def test_modebar(dash_br_driver):
    """Check that modebar element exist for the chart."""
    check_text(dash_br_driver, xpath=href_path(href=cnst.HOME_PAGE_PATH), text=cnst.HOME_PAGE)
    webdriver_click_waiter(dash_br_driver, xpath=nav_card_text_path(href=cnst.FILTERS_PAGE_PATH))
    webdriver_waiter(dash_br_driver, xpath="//*[@class='modebar-container']")
